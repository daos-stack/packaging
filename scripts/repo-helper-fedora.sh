#!/bin/bash
set -uex

# This script is used by Dockerfiles to optionally use
# a local repository instead of a distro provided repository.

: "${REPO_FILE_URL:=}"
: "${DAOS_LAB_CA_FILE_URL:=}"
: "${FVERSION:=latest}"
: "${REPOSITORY_NAME:=artifactory}"

is_fedora_eol() {
    local fedora_version
    fedora_version=$(grep VERSION_ID /etc/os-release | cut -d= -f2 | tr -d '"')
    local eol_date
    eol_date=$(curl -s https://endoflife.date/api/fedora.json | jq -r ".[] | select(.cycle == \"$fedora_version\") | .eol")
    if [[ -z "$eol_date" ]]; then
        return 0
    fi
    local today
    today=$(date +%Y-%m-%d)
    if [[ "$today" > "$eol_date" ]]; then
        return 0  # true: EOL
    else
        return 1  # false: not EOL
    fi
}

# shellcheck disable=SC2120
disable_repos () {
    local repos_dir="$1"
    local archive="${2:-}"
    shift
    local save_repos
    IFS=" " read -r -a save_repos <<< "${*:-} daos_ci-fedora${archive}-${REPOSITORY_NAME}"
    if [ -n "$REPO_FILE_URL" ]; then
        pushd "$repos_dir"
        local repo
        for repo in "${save_repos[@]}"; do
            mv "$repo".repo{,.tmp}
        done
        for file in *.repo; do
            true > "$file"
        done
        for repo in "${save_repos[@]}"; do
            mv "$repo".repo{.tmp,}
        done
        popd
    fi
}

# Use local repo server if present
install_curl() {
    :
}

# Use local repo server if present
install_optional_ca() {
    ca_storage="/etc/pki/ca-trust/source/anchors/"
    if [ -n "$DAOS_LAB_CA_FILE_URL" ]; then
        curl -k --noproxy '*' -sSf -o "${ca_storage}lab_ca_file.crt" \
            "$DAOS_LAB_CA_FILE_URL"
        update-ca-trust
    fi
}

# Use local repo server if present
# if a local repo server is present and the distro repo server can not
# be reached, have to bootstrap in an environment to get curl installed
# to then install the pre-built repo file.

if [ -n "$REPO_FILE_URL" ]; then
    install_curl
    install_optional_ca
    if is_fedora_eol; then
        archive="-archive"
    else
        archive=""
    fi

    mkdir -p /etc/yum.repos.d
    pushd /etc/yum.repos.d/
    curl -k --noproxy '*' -sSf                                  \
         -o "daos_ci-fedora${archive}-${REPOSITORY_NAME}.repo"  \
         "${REPO_FILE_URL}daos_ci-fedora${archive}-${REPOSITORY_NAME}.repo"
    disable_repos "/etc/yum.repos.d/" "${archive}"
    popd
fi
dnf -y install dnf-plugins-core
# This does not work in fedora/41 anymore -- needs investigation
# dnf -y config-manager --save --setopt=assumeyes=True
# dnf config-manager --save --setopt=install_weak_deps=False
dnf clean all

disable_repos /etc/yum.repos.d/ "${save_repos[@]}"
