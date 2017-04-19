#pragma once

#include <boost/preprocessor/control/if.hpp>
#include <boost/vmd/is_number.hpp>

#if defined(HYGENIC_DEMO_STATIC)
#define VIS_PUBLIC()
#define VIS_PRIVATE()
#define HYGENIC_DEMO_PRIVATE
#else
#if defined(_MSC_VER)
#define VIS_PUBLIC() __declspec(dllexport)
#define VIS_PRIVATE() __declspec(dllimport)
#define HYGENIC_DEMO_PRIVATE
#else
#define VIS_PUBLIC() __attribute__((visibility("default")))
#define VIS_PRIVATE() __attribute__((visibility("hidden")))
#define HYGENIC_DEMO_PRIVATE VIS_PRIVATE()
#endif
#endif

#define HYGENIC_DEMO_API_IMPL2(COND) BOOST_PP_IIF(COND, VIS_PUBLIC, VIS_PRIVATE)()
#define HYGENIC_DEMO_API_IMPL(ARG) HYGENIC_DEMO_API_IMPL2(BOOST_VMD_IS_NUMBER(ARG))
#define HYGENIC_DEMO_API(LIB) HYGENIC_DEMO_API_IMPL(HYGENIC_DEMO_API_ ## LIB)
