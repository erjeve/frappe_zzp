# Docker Bake configuration for RGS layer
# Usage: docker buildx bake -f images/rgs/docker-bake.hcl rgs

variable "ERPNEXT_VERSION" {
  default = "v15"
}

variable "RGS_VERSION" {
  default = "3.7"
}

group "default" {
  targets = ["rgs"]
}

target "rgs" {
  context = "."
  dockerfile = "images/rgs/Containerfile"
  args = {
    ERPNEXT_VERSION = ERPNEXT_VERSION
  }
  tags = [
    "frappe/erpnext:rgs-${RGS_VERSION}",
    "frappe/erpnext:rgs-latest"
  ]
  platforms = ["linux/amd64", "linux/arm64"]
}
