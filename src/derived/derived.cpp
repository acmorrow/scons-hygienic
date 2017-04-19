#include "derived/derived.h"

#include "impl/impl.h"

Derived::Derived() = default;

void Derived::_doIt() {
    return impl::doIt();
}
