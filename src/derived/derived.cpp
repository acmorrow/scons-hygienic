#include "derived/derived.h"

#include <cstdio>

Derived::Derived() = default;

void Derived::_doIt() {
    std::printf("Doing  it in Derived\n");
}
