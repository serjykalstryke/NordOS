#include "platform/power.h"

#include "base/event_loop.h"

#include <iostream>
#include <string_view>

int main(int argc, char** argv)
{
    if (argc == 2 && std::string_view(argv[1]) == "poweroff") {
        cutefish::base::EventLoop loop;
        if (nordos::platform::power::powerOff())
            return 0;
        std::cerr << "The system declined the shutdown request.\n";
        return 1;
    }

    std::cerr << "Usage: typewriter-power poweroff\n";
    return 2;
}
