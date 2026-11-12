// SPDX-FileCopyrightText: 2026 Reion Wong <reionwong@gmail.com>
// SPDX-License-Identifier: BSD-3-Clause

#pragma once

namespace nordos::platform::power {

// Wait for the platform to accept or reject each request. True reports
// acceptance. Completion may occur after the call returns.
bool reboot();
bool powerOff();
bool suspend();

} // namespace nordos::platform::power
