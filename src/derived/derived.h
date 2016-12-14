#pragma once

#include "base/base.h"

#include "config.h"

class HYGENIC_DEMO_API(LIBDERIVED) Derived : public Base {
public:
    Derived();

private:
    HYGENIC_DEMO_PRIVATE void _doIt() final;
};
