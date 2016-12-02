#pragma once

class Base {
public:

    Base(Base&) = delete;
    Base& operator=(Base&) = delete;

    virtual ~Base() = default;

    void doIt();

protected:
    Base() = default;

private:
    virtual void _doIt() = 0;
};
