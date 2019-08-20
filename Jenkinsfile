#!/usr/bin/groovy
/* Copyright (C) 2019 Intel Corporation
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted for any purpose (including commercial purposes)
 * provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions, and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions, and the following disclaimer in the
 *    documentation and/or materials provided with the distribution.
 *
 * 3. In addition, redistributions of modified forms of the source or binary
 *    code must carry prominent notices stating that the original code was
 *    changed and the date of the change.
 *
 *  4. All publications or advertising materials mentioning features or use of
 *     this software are asked, but not required, to acknowledge that it was
 *     developed by Intel Corporation and credit the contributors.
 *
 * 5. Neither the name of Intel Corporation, nor the name of any Contributor
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
// To use a test branch (i.e. PR) until it lands to master
// I.e. for testing library changes
//@Library(value="pipeline-lib@your_branch") _

pipeline {
    agent none

    stages {
        stage('Cancel Previous Builds') {
            when { changeRequest() }
            steps {
                cancelPreviousBuilds()
            }
        }
        stage('Build') {
            parallel {
                stage('Build libfabric on CentOS 7') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile.mockbuild'
                            label 'docker_runner'
                            args  '--group-add mock' +
                                  ' --cap-add=SYS_ADMIN' +
                                  ' --privileged=true'
                            additionalBuildArgs '--build-arg UID=$(id -u)' +
                                                ' --build-arg JENKINS_URL=' +
                                                env.JENKINS_URL
                         }
                    }
                    steps {
                        checkoutScm url: 'https://github.com/daos-stack/libfabric.git',
                                    checkoutDir: "libfabric"
                        sh label: env.STAGE_NAME,
                           script: '''rm -rf libfabric/packaging/
                                      mkdir libfabric/packaging/
                                      cp Dockerfile* Makefile_{distro_vars,packaging}.mk libfabric/packaging/
                                      cd libfabric/
                                      rm -rf artifacts/centos7/
                                      mkdir -p artifacts/centos7/
                                      make CHROOT_NAME="epel-7-x86_64" chrootbuild'''
                    }
                    post {
                        unsuccessful {
                            sh label: "Collect artifacts",
                               script: '''mockroot=/var/lib/mock/epel-7-x86_64
                                          artdir=$PWD/libfabric/artifacts/centos7
                                          cp -af _topdir/SRPMS $artdir
                                          (cd $mockroot/result/ &&
                                           cp -r . $artdir)
                                          (if cd $mockroot/root/builddir/build/BUILD/*/; then
                                           find . -name configure -printf %h\\\\n | \
                                           while read dir; do
                                               if [ ! -f $dir/config.log ]; then
                                                   continue
                                               fi
                                               tdir="$artdir/autoconf-logs/$dir"
                                               mkdir -p $tdir
                                               cp -a $dir/config.log $tdir/
                                           done
                                           fi)'''
                            archiveArtifacts artifacts: 'libfabric/artifacts/centos7/**'
                        }
                    }
                } //stage('Build libfabric on CentOS 7')
                stage('Build libfabric on Leap 15') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile.mockbuild'
                            label 'docker_runner'
                            args  '--group-add mock' +
                                  ' --cap-add=SYS_ADMIN' +
                                  ' --privileged=true'
                            additionalBuildArgs '--build-arg UID=$(id -u) ' +
                                                ' --build-arg JENKINS_URL=' +
                                                env.JENKINS_URL
                        }
                    }
                    steps {
                        checkoutScm url: 'https://github.com/daos-stack/libfabric.git',
                                    checkoutDir: "libfabric"
                        sh label: env.STAGE_NAME,
                           script: '''rm -rf libfabric/packaging/
                                      mkdir libfabric/packaging/
                                      cp Dockerfile* Makefile_{distro_vars,packaging}.mk libfabric/packaging/
                                      cd libfabric/
                                      rm -rf artifacts/leap15/
                                      mkdir -p artifacts/leap15/
                                      make chrootbuild'''
                    }
                    post {
                        unsuccessful {
                            sh label: "Collect artifacts",
                               script: '''mockbase=/var/tmp/build-root/home/abuild
                                          mockroot=$mockbase/rpmbuild
                                          artdir=$PWD/artifacts/leap15
                                          (if cd $mockroot/BUILD; then
                                           find . -name configure -printf %h\\\\n | \
                                           while read dir; do
                                               if [ ! -f $dir/config.log ]; then
                                                   continue
                                               fi
                                               tdir="$artdir/autoconf-logs/$dir"
                                               mkdir -p $tdir
                                               cp -a $dir/config.log $tdir/
                                               done
                                           fi)'''
                            archiveArtifacts artifacts: 'libfabric/artifacts/leap15/**'
                        }
                    }
                } //stage('Build libfabric on Leap 15')
                stage('Build libfabric on Ubuntu 18.04') {
                    when {
                        beforeAgent true
                        allOf {
                            // disable until we can get a "spectool" built for Ubuntu
                            expression { false }
                            expression { env.DAOS_STACK_REPO_PUB_KEY != null }
                            expression { env.DAOS_STACK_REPO_SUPPORT != null }
                            expression { env.DAOS_STACK_REPO_UBUNTU_18_04_LIST != null}
                        }
                    }
                    agent {
                        dockerfile {
                            filename 'Dockerfile.ubuntu.18.04'
                            label 'docker_runner'
                            args '--privileged=true'
                            additionalBuildArgs '--build-arg UID=$(id -u)'
                        }
                    }
                    steps {
                        checkoutScm url: 'https://github.com/daos-stack/libfabric.git',
                                    checkoutDir: "libfabric"
                        sh label: env.STAGE_NAME,
                           script: '''rm -rf libfabric/packaging/
                                      mkdir libfabric/packaging/
                                      cp Dockerfile* Makefile_{distro_vars,packaging}.mk libfabric/packaging/
                                      cd libfabric/
                                      rm -rf artifacts/ubuntu18.04/
                                      mkdir -p artifacts/ubuntu18.04/
                                      : "${DEBEMAIL:="$env.DAOS_EMAIL"}"
                                      : "${DEBFULLNAME:="$env.DAOS_FULLNAME"}"
                                      export DEBEMAIL
                                      export DEBFULLNAME
                                      make chrootbuild'''
                    }
                    post {
                        success {
                            sh '''cp -v \
                                   /var/cache/pbuilder/result/*{.buildinfo,.changes,.deb,.dsc,.gz,.xz} \
                                   artifacts/ubuntu18.04/
                                  pushd artifacts/ubuntu18.04/
                                    dpkg-scanpackages . /dev/null | \
                                      gzip -9c > Packages.gz
                                  popd'''
                        }
                        unsuccessful {
                            sh label: "Collect artifacts",
                               script: "cat /var/cache/pbuilder/result/*.buildinfo",
                               returnStatus: true
                        }
                    }
                } //stage('Build on Ubuntu 18.04')
                stage('Build on Ubuntu rolling') {
                    // Rolling is current Ubuntu release
                    when {
                        beforeAgent true
                        allOf {
                            // disable until we can get a "spectool" built for Ubuntu
                            expression { false }
                            expression { env.DAOS_STACK_REPO_PUB_KEY != null }
                            expression { env.DAOS_STACK_REPO_SUPPORT != null }
                            expression { env.DAOS_STACK_REPO_UBUNTU_18_04_LIST != null}
                        }
                    }
                    agent {
                        dockerfile {
                            filename 'Dockerfile.ubuntu.rolling'
                            label 'docker_runner'
                            args '--privileged=true'
                            additionalBuildArgs '--build-arg UID=$(id -u)'
                        }
                    }
                    steps {
                        checkoutScm url: 'https://github.com/daos-stack/libfabric.git',
                                    checkoutDir: "libfabric"
                        sh label: env.STAGE_NAME,
                           script: '''rm -rf libfabric/packaging/
                                      mkdir libfabric/packaging/
                                      cp Dockerfile* Makefile_packaging.mk libfabric/packaging/
                                      cd libfabric/
                                      rm -rf artifacts/ubuntu18.10/
                                      mkdir -p artifacts/ubuntu18.10/
                                      mkdir -p _topdir
                                      : "${DEBEMAIL:="$env.DAOS_EMAIL"}"
                                      : "${DEBFULLNAME:="$env.DAOS_FULLNAME"}"
                                      export DEBEMAIL
                                      export DEBFULLNAME
                                      make chrootbuild'''
                    }
                    post {
                        success {
                            sh '''cp -v \
                                   /var/cache/pbuilder/result/*{.buildinfo,.changes,.deb,.dsc,.gz,.xz} \
                                   artifacts/ubuntu_rolling/
                                  pushd artifacts/ubuntu_rolling/
                                    dpkg-scanpackages . /dev/null | \
                                      gzip -9c > Packages.gz
                                  popd'''
                        }
                        unsuccessful {
                            sh label: "Collect artifacts",
                               script: "cat /var/cache/pbuilder/result/*.buildinfo",
                               returnStatus: true
                        }
                        cleanup {
                            archiveArtifacts artifacts: 'artifacts/ubuntu_rolling/**'
                        }
                    }
                } //stage('Build on Ubuntu rolling') 
            }
        } //stage('Build')
    } // stages
} // pipeline
