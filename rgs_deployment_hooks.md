# RGS post-deployment hook options for frappe_docker

## Option 1: Init Container with Site Check (Recommended)
# Add to compose.rgs.yaml

  rgs-initializer:
    <<: *rgs_environment
    image: frappe/erpnext:rgs-latest
    command: >
      bash -c "
        echo '🇳🇱 RGS 3.7 Post-Deployment Initializer';
        echo 'Waiting for site to be available...';
        
        # Wait for site to exist
        while [ ! -d '/home/frappe/frappe-bench/sites/\$\$SITE_NAME' ]; do
          echo 'Waiting for site \$\$SITE_NAME to be created...';
          sleep 10;
        done;
        
        echo '✓ Site found! Installing RGS custom fields...';
        cd /home/frappe/frappe-bench;
        source env/bin/activate;
        
        # Check if RGS is already installed
        if python -c \"
import frappe;
frappe.init(site='\$\$SITE_NAME');
frappe.connect();
exists = frappe.db.exists('Custom Field', {'dt': 'Account', 'fieldname': 'rgs_code'});
frappe.destroy();
exit(0 if exists else 1)
        \"; then
          echo '✅ RGS custom fields already installed';
        else
          echo '🔧 Installing RGS custom fields...';
          python /home/frappe/rgs_scripts/add_complete_rgs.py;
          echo '✅ RGS installation completed!';
        fi;
        "
    volumes:
      - sites:/home/frappe/frappe-bench/sites
    depends_on:
      configurator:
        condition: service_completed_successfully
    restart: "no"  # Run once only
    profiles:
      - rgs

## Option 2: Service Health Check Hook
# Modify backend service to include RGS installation

  backend:
    healthcheck:
      test: |
        curl -f http://localhost:8000/api/method/ping &&
        ([ -f /tmp/rgs_installed ] || (
          cd /home/frappe/frappe-bench &&
          source env/bin/activate &&
          python /home/frappe/rgs_scripts/add_complete_rgs.py &&
          touch /tmp/rgs_installed
        ))
      interval: 30s
      timeout: 10s
      retries: 3

## Option 3: Entrypoint Hook (Most Integrated)
# Modify the RGS Containerfile to include a custom entrypoint

# In images/rgs/Containerfile:
COPY --chown=frappe:frappe images/rgs/rgs-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/rgs-entrypoint.sh"]
CMD ["gunicorn", "--chdir=/home/frappe/frappe-bench", ...]

## Option 4: Bench Command Hook
# Add to .env for manual installation:
# RGS_INSTALL_CMD=docker compose exec backend bash -c "cd /home/frappe/frappe-bench && source env/bin/activate && python /home/frappe/rgs_scripts/add_complete_rgs.py"
