// SPDX-FileCopyrightText: 2026 Reion Wong <reionwong@gmail.com>
// SPDX-License-Identifier: BSD-3-Clause

#include "platform/power.h"

#include "base/dbus.h"
#include "base/logging.h"

namespace dbus = cutefish::base::dbus;

namespace {

bool callLogind(const char* method)
{
    static const cutefish::base::LogCategory log("cutefish.session");
    dbus::Connection* bus = dbus::Connection::system();
    if (!bus) {
        CF_WARNING(log) << "logind" << method << "failed: no system bus";
        return false;
    }
    dbus::Message message = bus->newMethodCall("org.freedesktop.login1", "/org/freedesktop/login1",
                                               "org.freedesktop.login1.Manager", method);
    // Allow logind to request interactive authorization through Polkit.
    message.append(true);

    const dbus::Reply reply = bus->call(message);
    if (reply.isError()) {
        CF_WARNING(log) << "logind" << method << "failed:" << reply.error().name << reply.error().message;
        return false;
    }

    return true;
}

} // namespace

namespace nordos::platform::power {

bool reboot()
{
    return callLogind("Reboot");
}

bool powerOff()
{
    return callLogind("PowerOff");
}

bool suspend()
{
    return callLogind("Suspend");
}

} // namespace nordos::platform::power
