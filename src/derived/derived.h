#pragma once

#include "base.h"

class Derived : public Base {
private:
    void _doIt() final;
};
