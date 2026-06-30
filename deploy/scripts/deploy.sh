#!/bin/bash
set -euo pipefail

# ============================================================
# Docker + Nginx Multi-Site Deployment Script
# ============================================================
# Usage:
#   ./deploy.sh                    # Deploy all enabled sites
#   ./deploy.sh --site rag-knowledge  # Deploy specific site
#   ./deploy.sh --list             # List all sites
#   ./deploy.sh --status           # Show deployment status
#   ./deploy.sh --nginx-only       # Regenerate Nginx config only
#   ./deploy.sh --ssl <site>       # Setup SSL for a site
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
SITES_FILE="${DEPLOY_DIR}/sites.json"
NGINX_DIR="${DEPLOY_DIR}/nginx"
CERTS_DIR="${DEPLOY_DIR}/certs"
GENERATED_DIR="${DEPLOY_DIR}/generated"
LOG_DIR="${DEPLOY_DIR}/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================
# Utility Functions
# ============================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

check_dependencies() {
    local missing=()
    for cmd in docker jq; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing[*]}"
        log_info "Install with: apt-get install -y ${missing[*]}"
        exit 1
    fi
}

# ============================================================
# JSON Processing (using jq)
# ============================================================

get_global_config() {
    local key="$1"
    local default="${2:-}"
    local value
    value=$(jq -r ".global.${key} // empty" "$SITES_FILE")
    if [ -z "$value" ]; then
        echo "$default"
    else
        echo "$value"
    fi
}

get_site_config() {
    local site_name="$1"
    local key="$2"
    local default="${3:-}"
    local value
    value=$(jq -r ".sites[] | select(.name == \"${site_name}\") | .${key} // empty" "$SITES_FILE")
    if [ -z "$value" ]; then
        echo "$default"
    else
        echo "$value"
    fi
}

get_all_sites() {
    jq -r '.sites[].name' "$SITES_FILE"
}

get_enabled_sites() {
    jq -r '.sites[] | select(.enabled == true) | .name' "$SITES_FILE"
}

get_site_count() {
    jq '.sites | length' "$SITES_FILE"
}

# ============================================================
# Template Rendering (Mustache-like)
# ============================================================

render_template() {
    local template_file="$1"
    local output_file="$2"
    local site_name="${3:-}"

    # Read template
    local template
    template=$(cat "$template_file")

    # Replace global variables
    template="${template//\{\{nginx_http_port\}\}/$(get_global_config 'nginx_http_port' '80')}"
    template="${template//\{\{nginx_https_port\}\}/$(get_global_config 'nginx_https_port' '443')}"
    template="${template//\{\{worker_processes\}\}/$(get_global_config 'worker_processes' 'auto')}"
    template="${template//\{\{worker_connections\}\}/$(get_global_config 'worker_connections' '1024')}"
    template="${template//\{\{client_max_body_size\}\}/$(get_global_config 'client_max_body_size' '50m')}"
    template="${template//\{\{log_level\}\}/$(get_global_config 'log_level' 'warn')}"
    template="${template//\{\{ssl_protocols\}\}/$(get_global_config 'ssl_protocols' 'TLSv1.2 TLSv1.3')}"
    template="${template//\{\{ssl_ciphers\}\}/$(get_global_config 'ssl_ciphers' 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256')}"
    template="${template//\{\{proxy_connect_timeout\}\}/$(get_global_config 'proxy_connect_timeout' '60')}"
    template="${template//\{\{proxy_send_timeout\}\}/$(get_global_config 'proxy_send_timeout' '60')}"
    template="${template//\{\{proxy_read_timeout\}\}/$(get_global_config 'proxy_read_timeout' '60')}"

    # Handle gzip block
    local gzip_enabled
    gzip_enabled=$(get_global_config 'gzip' 'true')
    if [ "$gzip_enabled" = "true" ]; then
        local gzip_types
        gzip_types=$(get_global_config 'gzip_types' 'text/plain text/css application/json application/javascript')
        template="${template//\{\{#gzip\}\}/}"
        template="${template//\{\{\/gzip\}\}/}"
        template="${template//\{\{gzip_types\}\}/$gzip_types}"
    else
        # Remove gzip blocks
        template=$(echo "$template" | sed '/{{#gzip}}/,/{{\/gzip}}/d')
    fi

    # Handle site blocks
    local new_template=""
    local in_site_block=false
    local site_block=""
    local site_block_template=""

    while IFS= read -r line; do
        if [[ "$line" == *"{{#sites}}"* ]]; then
            in_site_block=true
            site_block=""
            continue
        fi
        if [[ "$line" == *"{{/sites}}"* ]]; then
            in_site_block=false
            # Process site block for each site
            local sites
            sites=$(get_enabled_sites)
            while IFS= read -r site; do
                if [ -n "$site" ]; then
                    local site_template="$site_block"
                    # Replace site variables
                    local site_domain site_port site_name_val site_ws site_static_cache
                    site_domain=$(get_site_config "$site" "domain")
                    site_port=$(get_site_config "$site" "upstream_port")
                    site_name_val=$(get_site_config "$site" "name")
                    site_ws=$(get_site_config "$site" "websocket" "false")
                    site_static_cache=$(get_site_config "$site" "static_cache_days" "7")

                    site_template="${site_template//\{\{name\}\}/$site_name_val}"
                    site_template="${site_template//\{\{domain\}\}/$site_domain}"
                    site_template="${site_template//\{\{upstream_port\}\}/$site_port}"

                    # Handle enabled flag
                    site_template="${site_template//\{\{#enabled\}\}/}"
                    site_template="${site_template//\{\{\/enabled\}\}/}"

                    # Handle websocket block
                    if [ "$site_ws" = "true" ]; then
                        site_template="${site_template//\{\{#websocket\}\}/}"
                        site_template="${site_template//\{\{\/websocket\}\}/}"
                    else
                        site_template=$(echo "$site_template" | sed '/{{#websocket}}/,/{{\/websocket}}/d')
                    fi

                    # Handle static cache block
                    if [ -n "$site_static_cache" ] && [ "$site_static_cache" != "0" ]; then
                        site_template="${site_template//\{\{#static_cache_days\}\}/}"
                        site_template="${site_template//\{\{\/static_cache_days\}\}/}"
                        site_template="${site_template//\{\{static_cache_days\}\}/$site_static_cache}"
                    else
                        site_template=$(echo "$site_template" | sed '/{{#static_cache_days}}/,/{{\/static_cache_days}}/d')
                    fi

                    # Handle access_log and error_log
                    local access_log error_log
                    access_log=$(get_site_config "$site" "access_log" "true")
                    error_log=$(get_site_config "$site" "error_log" "true")
                    if [ "$access_log" = "true" ]; then
                        site_template="${site_template//\{\{#access_log\}\}/}"
                        site_template="${site_template//\{\{\/access_log\}\}/}"
                    else
                        site_template=$(echo "$site_template" | sed '/{{#access_log}}/,/{{\/access_log}}/d')
                    fi
                    if [ "$error_log" = "true" ]; then
                        site_template="${site_template//\{\{#error_log\}\}/}"
                        site_template="${site_template//\{\{\/error_log\}\}/}"
                    else
                        site_template=$(echo "$site_template" | sed '/{{#error_log}}/,/{{\/error_log}}/d')
                    fi

                    # Handle custom headers
                    local x_frame x_content
                    x_frame=$(get_site_config "$site" "custom_headers.X-Frame-Options" "")
                    x_content=$(get_site_config "$site" "custom_headers.X-Content-Type-Options" "")
                    if [ -n "$x_frame" ] || [ -n "$x_content" ]; then
                        site_template="${site_template//\{\{#custom_headers\}\}/}"
                        site_template="${site_template//\{\{\/custom_headers\}\}/}"
                        if [ -n "$x_frame" ]; then
                            site_template="${site_template//\{\{#X-Frame-Options\}\}/}"
                            site_template="${site_template//\{\{\/X-Frame-Options\}\}/}"
                            site_template="${site_template//\{\{X-Frame-Options\}\}/$x_frame}"
                        else
                            site_template=$(echo "$site_template" | sed '/{{#X-Frame-Options}}/,/{{\/X-Frame-Options}}/d')
                        fi
                        if [ -n "$x_content" ]; then
                            site_template="${site_template//\{\{#X-Content-Type-Options\}\}/}"
                            site_template="${site_template//\{\{\/X-Content-Type-Options\}\}/}"
                            site_template="${site_template//\{\{X-Content-Type-Options\}\}/$x_content}"
                        else
                            site_template=$(echo "$site_template" | sed '/{{#X-Content-Type-Options}}/,/{{\/X-Content-Type-Options}}/d')
                        fi
                    else
                        site_template=$(echo "$site_template" | sed '/{{#custom_headers}}/,/{{\/custom_headers}}/d')
                    fi

                    new_template+="$site_template"$'\n'
                fi
            done <<< "$sites"
            continue
        fi
        if $in_site_block; then
            site_block+="$line"$'\n'
        else
            new_template+="$line"$'\n'
        fi
    done <<< "$template"

    # Clean up any remaining template markers
    new_template=$(echo "$new_template" | sed 's/{{[^}]*}}//g')

    echo "$new_template" > "$output_file"
}

# ============================================================
# Nginx Configuration Generation
# ============================================================

generate_nginx_config() {
    local site_filter="${1:-}"

    log_step "Generating Nginx configuration..."

    mkdir -p "$GENERATED_DIR"

    # Check if any site uses SSL
    local has_ssl=false
    while IFS= read -r site; do
        local ssl_enabled
        ssl_enabled=$(get_site_config "$site" "ssl" "false")
        if [ "$ssl_enabled" = "true" ]; then
            has_ssl=true
            break
        fi
    done <<< "$(get_enabled_sites)"

    # Generate appropriate config
    if $has_ssl; then
        render_template "${NGINX_DIR}/https.conf.template" "${GENERATED_DIR}/nginx.conf" "$site_filter"
        log_info "Generated HTTPS-enabled Nginx config"
    else
        render_template "${NGINX_DIR}/http.conf.template" "${GENERATED_DIR}/nginx.conf" "$site_filter"
        log_info "Generated HTTP-only Nginx config"
    fi

    log_success "Nginx config saved to ${GENERATED_DIR}/nginx.conf"
}

# ============================================================
# Docker Compose Generation
# ============================================================

generate_compose_file() {
    local site_name="$1"
    local project_path
    project_path=$(get_site_config "$site_name" "project_path")

    if [ -z "$project_path" ] || [ "$project_path" = "null" ]; then
        log_warn "No project_path configured for site: $site_name"
        return 1
    fi

    local compose_file="${project_path}/docker-compose.yml"
    if [ ! -f "$compose_file" ]; then
        log_warn "No docker-compose.yml found at: $compose_file"
        return 1
    fi

    log_info "Using compose file: $compose_file"
    echo "$compose_file"
}

# ============================================================
# SSL Certificate Management
# ============================================================

setup_ssl() {
    local site_name="$1"
    local domain
    domain=$(get_site_config "$site_name" "domain")

    if [ -z "$domain" ]; then
        log_error "No domain configured for site: $site_name"
        exit 1
    fi

    log_step "Setting up SSL for: $domain"

    local cert_dir="${CERTS_DIR}/${domain}"
    mkdir -p "$cert_dir"

    # Check if cert already exists
    if [ -f "${cert_dir}/fullchain.pem" ] && [ -f "${cert_dir}/privkey.pem" ]; then
        log_info "SSL certificates already exist for $domain"
        log_info "Certificate: ${cert_dir}/fullchain.pem"
        log_info "Private key: ${cert_dir}/privkey.pem"
        return 0
    fi

    # Generate self-signed certificate (for development/testing)
    log_info "Generating self-signed certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "${cert_dir}/privkey.pem" \
        -out "${cert_dir}/fullchain.pem" \
        -subj "/C=CN/ST=State/L=City/O=Organization/CN=${domain}" \
        2>/dev/null

    if [ $? -eq 0 ]; then
        log_success "Self-signed certificate generated for $domain"
        log_info "Certificate: ${cert_dir}/fullchain.pem"
        log_info "Private key: ${cert_dir}/privkey.pem"

        # Update sites.json with cert paths
        local tmp_file=$(mktemp)
        jq --arg site "$site_name" \
           --arg cert "${cert_dir}/fullchain.pem" \
           --arg key "${cert_dir}/privkey.pem" \
           '.sites |= map(if .name == $site then .ssl_cert_path = $cert | .ssl_key_path = $key | .ssl = true else . end)' \
           "$SITES_FILE" > "$tmp_file"
        mv "$tmp_file" "$SITES_FILE"

        log_info "Updated sites.json with SSL paths"
    else
        log_error "Failed to generate certificate"
        exit 1
    fi
}

# ============================================================
# Site Deployment
# ============================================================

deploy_site() {
    local site_name="$1"
    local domain project_path compose_profile container_name

    domain=$(get_site_config "$site_name" "domain")
    project_path=$(get_site_config "$site_name" "project_path")
    compose_profile=$(get_site_config "$site_name" "compose_profile" "")
    container_name=$(get_site_config "$site_name" "container_name")

    if [ -z "$project_path" ] || [ "$project_path" = "null" ]; then
        log_warn "Skipping site $site_name: no project_path configured"
        return 0
    fi

    log_step "Deploying site: $site_name ($domain)"

    # Check if docker-compose.yml exists
    if [ ! -f "${project_path}/docker-compose.yml" ]; then
        log_warn "No docker-compose.yml found at: $project_path"
        log_info "Skipping Docker deployment for $site_name"
        return 0
    fi

    # Build and start container
    cd "$project_path"

    local compose_cmd="docker compose"
    if [ -n "$compose_profile" ] && [ "$compose_profile" != "" ]; then
        compose_cmd="$compose_cmd --profile $compose_profile"
    fi

    log_info "Building and starting container..."
    $compose_cmd up -d --build 2>&1 | while IFS= read -r line; do
        echo "  $line"
    done

    if [ $? -eq 0 ]; then
        log_success "Site $site_name deployed successfully"
    else
        log_error "Failed to deploy site: $site_name"
        return 1
    fi
}

deploy_nginx() {
    log_step "Deploying Nginx..."

    # Check if Nginx container exists
    if docker ps -a --format '{{.Names}}' | grep -q "^nginx$"; then
        log_info "Reloading Nginx configuration..."
        docker exec nginx nginx -s reload 2>/dev/null || {
            log_warn "Failed to reload, restarting Nginx..."
            docker restart nginx
        }
    else
        log_info "Starting Nginx container..."
        docker run -d \
            --name nginx \
            --network host \
            -v "${GENERATED_DIR}/nginx.conf:/etc/nginx/nginx.conf:ro" \
            -v "${LOG_DIR}:/var/log/nginx" \
            --restart unless-stopped \
            nginx:alpine
    fi

    log_success "Nginx deployed successfully"
}

# ============================================================
# Status and Listing
# ============================================================

list_sites() {
    echo ""
    echo -e "${CYAN}Configured Sites:${NC}"
    echo "─────────────────────────────────────────────────────────────"
    printf "%-20s %-25s %-10s %-10s\n" "NAME" "DOMAIN" "PORT" "SSL"
    echo "─────────────────────────────────────────────────────────────"

    while IFS= read -r site; do
        local domain port ssl enabled
        domain=$(get_site_config "$site" "domain")
        port=$(get_site_config "$site" "upstream_port")
        ssl=$(get_site_config "$site" "ssl" "false")
        enabled=$(get_site_config "$site" "enabled" "true")

        local ssl_status="No"
        if [ "$ssl" = "true" ]; then
            ssl_status="Yes"
        fi

        local status_color="$GREEN"
        if [ "$enabled" != "true" ]; then
            status_color="$YELLOW"
        fi

        printf "%s%-20s%s %-25s %-10s %-10s\n" "$status_color" "$site" "$NC" "$domain" "$port" "$ssl_status"
    done <<< "$(get_all_sites)"

    echo "─────────────────────────────────────────────────────────────"
    echo ""
}

show_status() {
    echo ""
    echo -e "${CYAN}Deployment Status:${NC}"
    echo "─────────────────────────────────────────────────────────────"

    # Check Docker
    if docker info &> /dev/null; then
        echo -e "Docker:          ${GREEN}Running${NC}"
    else
        echo -e "Docker:          ${RED}Not Running${NC}"
    fi

    # Check Nginx container
    if docker ps --format '{{.Names}}' | grep -q "^nginx$"; then
        echo -e "Nginx:           ${GREEN}Running${NC}"
    else
        echo -e "Nginx:           ${YELLOW}Not Running${NC}"
    fi

    echo ""
    echo -e "${CYAN}Container Status:${NC}"
    echo "─────────────────────────────────────────────────────────────"
    printf "%-20s %-15s %-15s\n" "SITE" "STATUS" "PORT"
    echo "─────────────────────────────────────────────────────────────"

    while IFS= read -r site; do
        local container_name port
        container_name=$(get_site_config "$site" "container_name")
        port=$(get_site_config "$site" "upstream_port")

        local status="Stopped"
        local status_color="$RED"

        if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
            status="Running"
            status_color="$GREEN"
        elif docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
            status="Exited"
            status_color="$YELLOW"
        fi

        printf "%-20s %s%-15s%s %-15s\n" "$site" "$status_color" "$status" "$NC" "$port"
    done <<< "$(get_enabled_sites)"

    echo "─────────────────────────────────────────────────────────────"
    echo ""
}

# ============================================================
# Main Deployment Flow
# ============================================================

deploy_all() {
    local site_filter="${1:-}"

    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  Docker + Nginx Multi-Site Deployment${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""

    # Check dependencies
    check_dependencies

    # Validate sites.json
    if ! jq empty "$SITES_FILE" 2>/dev/null; then
        log_error "Invalid JSON in sites.json"
        exit 1
    fi

    # Create log directory
    mkdir -p "$LOG_DIR"

    # Generate Nginx config
    generate_nginx_config "$site_filter"

    # Deploy sites
    if [ -n "$site_filter" ]; then
        deploy_site "$site_filter"
    else
        while IFS= read -r site; do
            deploy_site "$site"
        done <<< "$(get_enabled_sites)"
    fi

    # Deploy Nginx
    deploy_nginx

    echo ""
    log_success "Deployment completed!"
    echo ""
    show_status
}

# ============================================================
# CLI Entry Point
# ============================================================

main() {
    case "${1:-}" in
        --list)
            list_sites
            ;;
        --status)
            show_status
            ;;
        --site)
            if [ -z "${2:-}" ]; then
                log_error "Please specify site name"
                exit 1
            fi
            deploy_all "$2"
            ;;
        --nginx-only)
            generate_nginx_config
            deploy_nginx
            ;;
        --ssl)
            if [ -z "${2:-}" ]; then
                log_error "Please specify site name"
                exit 1
            fi
            setup_ssl "$2"
            ;;
        --help|-h)
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  (no args)              Deploy all enabled sites"
            echo "  --site <name>          Deploy specific site"
            echo "  --list                 List all configured sites"
            echo "  --status               Show deployment status"
            echo "  --nginx-only           Regenerate Nginx config only"
            echo "  --ssl <site>           Setup SSL for a site"
            echo "  --help, -h             Show this help message"
            echo ""
            ;;
        *)
            deploy_all
            ;;
    esac
}

main "$@"
