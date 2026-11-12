// SPDX-License-Identifier: BSD-3-Clause

#include "platform/power.h"

#include "base/dbus.h"
#include "base/event_loop.h"

#include <cstdlib>
#include <future>
#include <iostream>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace dbus = cutefish::base::dbus;
namespace power = nordos::platform::power;
using cutefish::base::EventLoop;

int main()
{
    // CTest starts dbus-run-session, whose private bus also stands in for the system bus.
    const char* address = std::getenv("DBUS_SESSION_BUS_ADDRESS");
    if (!address || !*address || ::setenv("DBUS_SYSTEM_BUS_ADDRESS", address, 1) != 0) {
        std::cerr << "Cannot set up the private test bus\n";
        return 1;
    }

    std::promise<EventLoop*> ready;
    auto readyResult = ready.get_future();
    std::vector<std::pair<std::string, bool>> requests;
    std::thread server([&] {
        EventLoop loop;
        auto bus = dbus::Connection::open(dbus::Connection::Bus::Session, &loop);
        if (!bus) {
            ready.set_value(nullptr);
            return;
        }

        dbus::Object logind(bus.get(), "/org/freedesktop/login1", "org.freedesktop.login1.Manager");
        for (const char* method : {"Reboot", "PowerOff", "Suspend"}) {
            logind.addMethod(method, "b", "", [&, method](dbus::MethodCall& call) {
                bool interactive = false;
                const bool readArgument = call.read(interactive);
                requests.emplace_back(method, readArgument && interactive);
                if (requests.size() == 4) {
                    call.replyError("org.freedesktop.DBus.Error.AccessDenied", "Power request refused");
                } else {
                    call.reply();
                }
            });
        }

        const bool published = logind.publish() && bus->requestName("org.freedesktop.login1");
        ready.set_value(published ? &loop : nullptr);
        if (published)
            loop.run();
    });

    EventLoop* serverLoop = readyResult.get();
    if (!serverLoop) {
        server.join();
        std::cerr << "Cannot publish the test login1 service\n";
        return 1;
    }

    EventLoop clientLoop;
    const bool rebootAccepted = power::reboot();
    const bool powerOffAccepted = power::powerOff();
    const bool suspendAccepted = power::suspend();
    const bool refusedRequestAccepted = power::suspend();

    serverLoop->post([serverLoop] { serverLoop->quit(); });
    server.join();

    const std::vector<std::pair<std::string, bool>> expected {
        {"Reboot", true}, {"PowerOff", true}, {"Suspend", true}, {"Suspend", true},
    };
    if (requests != expected) {
        std::cerr << "Expected each power method to send the interactive authorization flag\n";
        return 1;
    }
    if (!rebootAccepted || !powerOffAccepted || !suspendAccepted || refusedRequestAccepted) {
        std::cerr << "Expected successful replies to report acceptance and a D-Bus error to report failure\n";
        return 1;
    }
}
