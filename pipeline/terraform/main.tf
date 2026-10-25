variable "environment" { type = string }
variable "max_db_connections" {
  type    = number
  default = 400
}

module "namespaces" {
  source      = "./modules/namespaces"
  environment = var.environment
  names       = var.environment == "production" ? ["novapay-prod-blue", "novapay-prod-green", "novapay-shared"] : ["novapay-${var.environment}"]
}

# Pool-budget guard: each colour may use at most 60% of max connections
output "per_colour_connection_budget" { value = floor(var.max_db_connections * 0.6) }
