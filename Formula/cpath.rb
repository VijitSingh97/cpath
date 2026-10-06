class Cpath < Formula
  desc "Copy a file's absolute path to the clipboard"
  homepage "https://github.com/VijitSingh97/cpath"
  url "https://github.com/VijitSingh97/cpath/archive/refs/tags/v0.0.1.tar.gz"
  sha256 "4cf7b44bad01f53f6a3f704e093d867aa5ed12939d4a808f86cc2b2874aee201"
  license "MIT"

  def install
    bin.install "bin/cpath"
    zsh_completion.install "completions/_cpath"
  end

  test do
    assert_match "cpath 0.0.1", shell_output("#{bin}/cpath --version")
    assert_match "file doesn't exist", shell_output("#{bin}/cpath #{testpath}/missing 2>&1", 1)
  end
end
