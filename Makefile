NAME    := libfabric
SRC_EXT := gz
SOURCE   = https://github.com/ofiwg/$(NAME)/archive/v$(VERSION).tar.$(SRC_EXT)

sle12_REPOS := --repo https://download.opensuse.org/repositories/science:/HPC/openSUSE_Leap_42.3/
sl42_REPOS  := --repo https://download.opensuse.org/repositories/science:/HPC/openSUSE_Leap_42.3/

include Makefile_packaging.mk
