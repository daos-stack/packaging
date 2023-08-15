#!/usr/bin/groovy
/* groovylint-disable DuplicateMapLiteral, DuplicateStringLiteral, NestedBlockDepth */
/* Copyright (C) 2019-2022 Intel Corporation
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

String updatePackaging(String dir) {
    return """rm -rf ${dir}/packaging/
              mkdir ${dir}/packaging/
              cp Dockerfile* Makefile_{distro_vars,packaging}.mk *_chrootbuild ${dir}/packaging/
              cd ${dir}/"""
}

/* groovylint-disable-next-line CompileStatic */
pipeline {
    agent { label 'lightweight' }

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
                            additionalBuildArgs '--build-arg PACKAGINGDIR=. ' + dockerBuildArgs()
                         }
                    }
                    steps {
                        checkoutScm url: 'https://github.com/daos-stack/libfabric.git',
                                    checkoutDir: 'libfabric',
                                    branch: commitPragma(pragma: 'libfabric-branch', def_val: 'master')
                        sh label: env.STAGE_NAME,
                           script: updatePackaging('libfabric') + '''
                                   rm -rf artifacts/centos7/
                                   mkdir -p artifacts/centos7/
                                   make CHROOT_NAME="centos+epel-7-x86_64" chrootbuild'''
                    }
                    post {
                        success {
                            sh 'ls -l /var/lib/mock/centos+epel-7-x86_64/result/'
                        }
                        unsuccessful {
                            sh label: 'Collect artifacts',
                               script: '''mockroot=/var/lib/mock/centos+epel-7-x86_64
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
            }
        } //stage('Build')
    } // stages
} // pipeline
