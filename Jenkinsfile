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
        stage('Lint') {
            stages {
                stage('RPM Lint') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile.centos.7'
                            label 'docker_runner'
                            args  '--group-add mock' +
                                  ' --cap-add=SYS_ADMIN' +
                                  ' --privileged=true'
                            additionalBuildArgs  '--build-arg UID=$(id -u)'
                        }
                    }
                    steps {
                        sh 'make rpmlint'
                    }
                }
            }
        } //stage('Lint')
        stage('Build') {
            parallel {
                stage('Build on CentOS 7') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile.centos.7'
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
                        sh '''rm -rf artifacts/centos7/
                              mkdir -p artifacts/centos7/
                              make chrootbuild'''
                    }
                    post {
                        success {
                            sh '''(cd /var/lib/mock/epel-7-x86_64/result/ &&
                                   cp -r . $OLDPWD/artifacts/centos7/)
                                  createrepo artifacts/centos7/'''
                        }
                        unsuccessful {
                            sh '''mockroot=/var/lib/mock/epel-7-x86_64
                                  artdir=$PWD/artifacts/centos7
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
                        }
                        cleanup {
                            archiveArtifacts artifacts: 'artifacts/centos7/**'
                        }
                    }
                } //stage('Build on CentOS 7')
                stage('Build on SLES 12.3') {
                    when {
                        beforeAgent true
                        environment name: 'SLES12_3_DOCKER', value: 'true'
                    }
                    agent {
                        dockerfile {
                            filename 'Dockerfile.sles.12.3'
                            label 'docker_runner'
                            args '--privileged=true'
                            additionalBuildArgs '--build-arg UID=$(id -u) ' +
                                                ' --build-arg JENKINS_URL=' +
                                                env.JENKINS_URL
                        }
                    }
                    steps {
                        sh '''rm -rf artifacts/sles12.3/
                              mkdir -p artifacts/sles12.3/
                              make chrootbuild'''
                    }
                    post {
                        success {
                            sh '''mockbase=/var/tmp/build-root/home/abuild
                                  mockroot=$mockbase/rpmbuild
                                  artdir=$PWD/artifacts/sles12.3
                                  (cd $mockroot &&
                                   cp {RPMS/*,SRPMS}/* $artdir)
                                  createrepo $artdir/'''
                        }
                        unsuccessful {
                            sh '''mockbase=/var/tmp/build-root/home/abuild
                                  mockroot=$mockbase/rpmbuild
                                  artdir=$PWD/artifacts/sles12.3
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
                        }
                        cleanup {
                            archiveArtifacts artifacts: 'artifacts/sles12.3/**'
                        }
                    }
                } //stage('Build on SLES 12.3')
                stage('Build on Leap 42.3') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile.leap.42.3'
                            label 'docker_runner'
                            args '--privileged=true'
                            additionalBuildArgs '--build-arg UID=$(id -u) ' +
                                                ' --build-arg JENKINS_URL=' +
                                                env.JENKINS_URL
                        }
                    }
                    steps {
                        sh '''rm -rf artifacts/leap42.3/
                              mkdir -p artifacts/leap42.3/
                              make chrootbuild'''
                    }
                    post {
                        success {
                            sh '''mockbase=/var/tmp/build-root/home/abuild
                                  mockroot=$mockbase/rpmbuild
                                  artdir=$PWD/artifacts/leap42.3
                                  (cd $mockroot &&
                                   cp {RPMS/*,SRPMS}/* $artdir)
                                  createrepo $artdir/'''
                        }
                        unsuccessful {
                            sh '''mockbase=/var/tmp/build-root/home/abuild
                                  mockroot=$mockbase/rpmbuild
                                  artdir=$PWD/artifacts/leap42.3
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
                        }
                        cleanup {
                            archiveArtifacts artifacts: 'artifacts/leap42.3/**'
                        }
                    }
                } //stage('Build on Leap 42.3')
                stage('Build on Leap 15') {
                    agent {
                        dockerfile {
                            filename 'Dockerfile.leap.15'
                            label 'docker_runner'
                            args '--privileged=true'
                            additionalBuildArgs '--build-arg UID=$(id -u) ' +
                                                ' --build-arg JENKINS_URL=' +
                                                env.JENKINS_URL
                        }
                    }
                    steps {
                        sh '''rm -rf artifacts/leap15/
                              mkdir -p artifacts/leap15/
                              make chrootbuild'''
                    }
                    post {
                        success {
                            sh '''mockbase=/var/tmp/build-root/home/abuild
                                  mockroot=$mockbase/rpmbuild
                                  artdir=$PWD/artifacts/leap15
                                  (cd $mockroot &&
                                   cp {RPMS/*,SRPMS}/* $artdir)
                                  createrepo $artdir/'''
                        }
                        unsuccessful {
                            sh '''mockbase=/var/tmp/build-root/home/abuild
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
                        }
                        cleanup {
                            archiveArtifacts artifacts: 'artifacts/leap15/**'
                        }
                    }
                } //stage('Build on Leap 15')
                // Ubuntu packaging builds currently require a repository
                stage('Build on Ubuntu 18.04') {
                    when {
                        beforeAgent true
                        allOf {
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
                            additionalBuildArgs '--build-arg UID=$(id -u) ' +
                                                ' --build-arg DAOS_PUB_KEY=' +
                                                env.DAOS_STACK_REPO_PUB_KEY +
                                                ' --build-arg DAOS_REPO_SUP=' +
                                                env.DAOS_STACK_REPO_SUPPORT +
                                                ' --build-arg DAOS_REPO=' +
                                                env.DAOS_STACK_REPO_UBUNTU_18_04_LIST

                        }
                    }
                    steps {
                        sh '''rm -rf artifacts/ubuntu18.04/
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
                            sh script: "cat /var/cache/pbuilder/result/*.buildinfo",
                               returnStatus: true
                            
                        }
                        cleanup {
                            archiveArtifacts artifacts: 'artifacts/ubuntu18.04/**'
                        }
                    }
                } //stage('Build on Ubuntu 18.04')
                stage('Build on Ubuntu rolling') {
                    // Rolling is current Ubuntu release
                    when {
                        beforeAgent true
                        allOf {
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
                            additionalBuildArgs '--build-arg UID=$(id -u) ' +
                                                ' --build-arg DAOS_PUB_KEY=' +
                                                env.DAOS_STACK_REPO_PUB_KEY +
                                                ' --build-arg DAOS_REPO_SUP=' +
                                                env.DAOS_STACK_REPO_SUPPORT +
                                                ' --build-arg DAOS_REPO=' +
                                                env.DAOS_STACK_REPO_UBUNTU_18_04_LIST
                        }
                    }
                    steps {
                        sh '''rm -rf artifacts/ubuntu_rolling/
                              mkdir -p artifacts/ubuntu_rolling/
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
                            sh script: "cat /var/cache/pbuilder/result/*.buildinfo",
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
