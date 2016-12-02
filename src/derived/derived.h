#pragma once

#include "../base/base.h"

class Derived : public Base {
private:
    void _doIt() final;
};
