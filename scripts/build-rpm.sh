#!/bin/bash

set -e  # Exit on any error

# Script constants
SPEC_FILE="tweaks-lite.spec"
BUILD_ROOT="$HOME/rpmbuild"
SOURCE_DIR="$(pwd)"
VERSION=$(grep "Version:" $SPEC_FILE | awk '{print $2}')

# Print colored status messages
print_status() {
    echo -e "\033[1;34m=> $1\033[0m"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking build requirements..."
    
    local required_tools=("rpmbuild" "rpmdev-setuptree")
    local missing_tools=()

    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done

    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo "Error: Missing required tools: ${missing_tools[*]}"
        echo "Please install rpm-build and rpmdevtools packages:"
        echo "sudo dnf install rpm-build rpmdevtools"
        exit 1
    fi
}

# Setup RPM build environment
setup_build_env() {
    print_status "Setting up RPM build environment..."
    rpmdev-setuptree
}

# Create source tarball
create_tarball() {
    print_status "Creating source tarball..."
    local tarball_name="tweaks-lite-${VERSION}.tar.gz"
    
    # Create a temporary directory for the source
    local temp_dir=$(mktemp -d)
    local project_dir="$temp_dir/tweaks-lite-${VERSION}"
    
    # Copy source files to temporary directory
    mkdir -p "$project_dir"
    cp -r * "$project_dir"
    
    # Create tarball
    cd "$temp_dir"
    tar czf "$BUILD_ROOT/SOURCES/$tarball_name" "tweaks-lite-${VERSION}"
    cd "$SOURCE_DIR"
    
    # Cleanup
    rm -rf "$temp_dir"
}

# Build the RPM
build_rpm() {
    print_status "Building RPM package..."
    rpmbuild -ba "$SPEC_FILE"
    
    if [ $? -eq 0 ]; then
        print_status "RPM build completed successfully!"
        echo "RPMs can be found in: $BUILD_ROOT/RPMS/"
        echo "Source RPM can be found in: $BUILD_ROOT/SRPMS/"
    else
        echo "Error: RPM build failed!"
        exit 1
    fi
}

# Main execution
main() {
    print_status "Starting RPM build process for Tweaks Lite..."
    
    check_requirements
    setup_build_env
    create_tarball
    build_rpm
}

main 
