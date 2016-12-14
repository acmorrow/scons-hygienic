#pragma once

#include "config.h"

class HYGENIC_DEMO_API(LIBBASE) Base {
public:

    Base(Base&) = delete;
    Base& operator=(Base&) = delete;

    virtual ~Base() = default;

    void doIt();

protected:
    Base();

private:
    HYGENIC_DEMO_PRIVATE virtual void _doIt() = 0;
};
