#include <cstdlib>

#include "derived/derived.h"

class XBase {
public:
    virtual ~XBase() = default;
};

class XDerived : public XBase {
private:
    ~XDerived() override = default;
};

int main() {
    Derived().doIt();
    return EXIT_SUCCESS;
}
