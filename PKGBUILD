# Maintainer: Karthikeyan K 
pkgname=padam-cli
pkgver=0.6.1
pkgrel=1
pkgdesc="Browse and play Tamil movies within your terminal"
arch=('x86_64')
url="https://github.com/e-Zephyr/padam-cli.git"
license=('MIT')
depends=('glibc') 
makedepends=('python' 'uv')
source=("$pkgname-$pkgver.tar.gz::https://github.com/e-Zephyr/padam-cli/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$pkgname-$pkgver"
    uv venv
    source .venv/bin/activate
    
    # Install dependencies and dev dependencies (including pyinstaller)
    uv pip install .
    uv pip install pyinstaller
    
    # Build the standalone binary
    pyinstaller --onefile --name "$pkgname" main.py
}

package() {
    cd "$pkgname-$pkgver"
    
    # Install the compiled binary into the system bin directory
    install -Dm755 "dist/$pkgname" "$pkgdir/usr/bin/$pkgname"
    
    # Install the license and readme
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
}