NAME    := libfabric
SRC_EXT := gz
SOURCE   = https://github.com/ofiwg/$(NAME)/archive/v$(VERSION).tar.$(SRC_EXT)

sle12_REPOS := --repo https://download.opensuse.org/repositories/science:/HPC/openSUSE_Leap_42.3/
sl42_REPOS  := --repo https://download.opensuse.org/repositories/science:/HPC/openSUSE_Leap_42.3/

ifneq ($(DAOS_STACK_REPO_SUPPORT),"")
ifneq ($(DAOS_STACK_REPO_UBUNTU_18_04_LIST),"")
ubuntu1804_REPOS := $(shell curl $(DAOS_STACK_REPO_SUPPORT)$(DAOS_STACK_REPO_UBUNTU_18_04_LIST))
# Additional repos can be added but must be separated by a | character.
endif
# Need to figure out how to support multiple keys, such as for IPMCTL
ifneq ($(DAOS_STACK_REPO_PUB_KEY),"")
ubuntu1804_KEY = /tmp/daos-stack-public.key
endif
endif
include Makefile_packaging.mk
