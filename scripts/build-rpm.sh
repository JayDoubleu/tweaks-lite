#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT="tweaks-lite"
VERSION="1.0.0"
SPEC_FILE="${PROJECT}.spec"
TARBALL="${PROJECT}-${VERSION}.tar.gz"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building RPM for ${PROJECT} v${VERSION}${NC}"

# Ensure rpmbuild directories exist
echo "Setting up RPM build environment..."
rpmdev-setuptree

# Create source tarball using git
echo "Creating source tarball..."
git archive --format=tar.gz --prefix="${PROJECT}-${VERSION}/" \
    -o ~/rpmbuild/SOURCES/${TARBALL} HEAD

# Copy spec file
echo "Copying spec file..."
cp ${SPEC_FILE} ~/rpmbuild/SPECS/

# Build RPM
echo "Building RPM..."
rpmbuild -ba ~/rpmbuild/SPECS/${SPEC_FILE}

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Build successful!${NC}"
    echo "RPMs can be found in:"
    echo "  ~/rpmbuild/RPMS/noarch/"
    echo "  ~/rpmbuild/SRPMS/"
    
    # List the built RPMs
    echo -e "\nBuilt packages:"
    ls -1 ~/rpmbuild/RPMS/noarch/${PROJECT}*.rpm
    ls -1 ~/rpmbuild/SRPMS/${PROJECT}*.rpm
else
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi 
