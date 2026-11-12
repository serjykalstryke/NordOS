// SPDX-License-Identifier: BSD-3-Clause

#include "autostartentries.h"

#include <iostream>

int main()
{
    const struct {
        const char* executable;
        bool startedBySession;
    } cases[] = {
        {"/opt/nordos/bin/nordos-test-compositor", true},
        {"nordos-test-compositor", true},
        {"/opt/nordos/bin/nordos-test-file-surface", true},
        {"nordos-test-authorization-agent", true},
        {"nordos-test-runtime", true},
        {"cutefish-services", true},
        {"xdg-user-dirs-update", true},
        {"/usr/bin/cutefish-compositor", false},
        {"cutefish-filemanager", false},
        {"cutefish-polkit-agent", false},
        {"cutefish-appruntime", false},
        {"nordos-test-runtime-helper", false},
    };

    for (const auto& test : cases) {
        if (isStartedBySession(test.executable) != test.startedBySession) {
            std::cerr << "Unexpected session ownership for " << test.executable << '\n';
            return 1;
        }
    }
}
