# Optional Route 53 configuration for domain management
# Uncomment and configure if you want Terraform to manage DNS records

# Data source for existing hosted zone (if domain is already in Route 53)
# data "aws_route53_zone" "main" {
#   name         = var.domain_name
#   private_zone = false
# }

# Route 53 A record for main domain (frontend)
# resource "aws_route53_record" "frontend" {
#   count   = var.domain_name != "" ? 1 : 0
#   zone_id = data.aws_route53_zone.main.zone_id
#   name    = var.domain_name
#   type    = "A"
#
#   alias {
#     name                   = aws_lb.main.dns_name
#     zone_id                = aws_lb.main.zone_id
#     evaluate_target_health = true
#   }
# }

# Route 53 A record for API subdomain (backend)
# resource "aws_route53_record" "api" {
#   count   = var.domain_name != "" ? 1 : 0
#   zone_id = data.aws_route53_zone.main.zone_id
#   name    = var.api_domain != "" ? var.api_domain : "api.${var.domain_name}"
#   type    = "A"
#
#   alias {
#     name                   = aws_lb.main.dns_name
#     zone_id                = aws_lb.main.zone_id
#     evaluate_target_health = true
#   }
# }

