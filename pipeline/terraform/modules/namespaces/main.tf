variable "environment" { type = string }
variable "names" { type = list(string) }

resource "kubernetes_namespace" "this" {
  for_each = toset(var.names)
  metadata {
    name = each.value
    labels = {
      "istio-injection"                    = "enabled"
      "pod-security.kubernetes.io/enforce" = "restricted"
      "novapay/environment"                = var.environment
    }
  }
}

resource "kubernetes_resource_quota" "this" {
  for_each = toset(var.names)
  metadata {
    name      = "quota"
    namespace = kubernetes_namespace.this[each.value].metadata[0].name
  }
  spec {
    hard = { "requests.cpu" = "100", "requests.memory" = "200Gi", "pods" = "500" }
  }
}
