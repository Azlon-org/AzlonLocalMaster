#!/bin/bash

# Database Export Script
# This script connects once to MySQL and exports all tables to separate CSV files

echo "Starting database export..."

# Create the SQL commands file
cat > export_commands.sql << 'EOF'
-- Set CSV output format
SET SESSION sql_mode = '';

-- Export each table with clear separators
SELECT 'TABLE_START:activity_logs' as marker;
SELECT * FROM activity_logs;
SELECT 'TABLE_END:activity_logs' as marker;

SELECT 'TABLE_START:admin_secret_phrase' as marker;
SELECT * FROM admin_secret_phrase;
SELECT 'TABLE_END:admin_secret_phrase' as marker;

SELECT 'TABLE_START:booking_issues' as marker;
SELECT * FROM booking_issues;
SELECT 'TABLE_END:booking_issues' as marker;

SELECT 'TABLE_START:booking_notes' as marker;
SELECT * FROM booking_notes;
SELECT 'TABLE_END:booking_notes' as marker;

SELECT 'TABLE_START:chat_users' as marker;
SELECT * FROM chat_users;
SELECT 'TABLE_END:chat_users' as marker;

SELECT 'TABLE_START:chats' as marker;
SELECT * FROM chats;
SELECT 'TABLE_END:chats' as marker;

SELECT 'TABLE_START:check_list_content' as marker;
SELECT * FROM check_list_content;
SELECT 'TABLE_END:check_list_content' as marker;

SELECT 'TABLE_START:clients' as marker;
SELECT * FROM clients;
SELECT 'TABLE_END:clients' as marker;

SELECT 'TABLE_START:exported_record' as marker;
SELECT * FROM exported_record;
SELECT 'TABLE_END:exported_record' as marker;

SELECT 'TABLE_START:extra_services' as marker;
SELECT * FROM extra_services;
SELECT 'TABLE_END:extra_services' as marker;

SELECT 'TABLE_START:fleet_alerts' as marker;
SELECT * FROM fleet_alerts;
SELECT 'TABLE_END:fleet_alerts' as marker;

SELECT 'TABLE_START:issues' as marker;
SELECT * FROM issues;
SELECT 'TABLE_END:issues' as marker;

SELECT 'TABLE_START:lead_sources' as marker;
SELECT * FROM lead_sources;
SELECT 'TABLE_END:lead_sources' as marker;

SELECT 'TABLE_START:message_attachments' as marker;
SELECT * FROM message_attachments;
SELECT 'TABLE_END:message_attachments' as marker;

SELECT 'TABLE_START:messages' as marker;
SELECT * FROM messages;
SELECT 'TABLE_END:messages' as marker;

SELECT 'TABLE_START:migrations' as marker;
SELECT * FROM migrations;
SELECT 'TABLE_END:migrations' as marker;

SELECT 'TABLE_START:notification_open_rate' as marker;
SELECT * FROM notification_open_rate;
SELECT 'TABLE_END:notification_open_rate' as marker;

SELECT 'TABLE_START:notifications' as marker;
SELECT * FROM notifications;
SELECT 'TABLE_END:notifications' as marker;

SELECT 'TABLE_START:operator_availability' as marker;
SELECT * FROM operator_availability;
SELECT 'TABLE_END:operator_availability' as marker;

SELECT 'TABLE_START:operator_balance' as marker;
SELECT * FROM operator_balance;
SELECT 'TABLE_END:operator_balance' as marker;

SELECT 'TABLE_START:operator_code' as marker;
SELECT * FROM operator_code;
SELECT 'TABLE_END:operator_code' as marker;

SELECT 'TABLE_START:operator_compensation' as marker;
SELECT * FROM operator_compensation;
SELECT 'TABLE_END:operator_compensation' as marker;

SELECT 'TABLE_START:operator_documents' as marker;
SELECT * FROM operator_documents;
SELECT 'TABLE_END:operator_documents' as marker;

SELECT 'TABLE_START:operator_payouts' as marker;
SELECT * FROM operator_payouts;
SELECT 'TABLE_END:operator_payouts' as marker;

SELECT 'TABLE_START:operator_settings' as marker;
SELECT * FROM operator_settings;
SELECT 'TABLE_END:operator_settings' as marker;

SELECT 'TABLE_START:operators' as marker;
SELECT * FROM operators;
SELECT 'TABLE_END:operators' as marker;

SELECT 'TABLE_START:orders' as marker;
SELECT * FROM orders;
SELECT 'TABLE_END:orders' as marker;

SELECT 'TABLE_START:otp' as marker;
SELECT * FROM otp;
SELECT 'TABLE_END:otp' as marker;

SELECT 'TABLE_START:people_notified' as marker;
SELECT * FROM people_notified;
SELECT 'TABLE_END:people_notified' as marker;

SELECT 'TABLE_START:permission_category' as marker;
SELECT * FROM permission_category;
SELECT 'TABLE_END:permission_category' as marker;

SELECT 'TABLE_START:permissions' as marker;
SELECT * FROM permissions;
SELECT 'TABLE_END:permissions' as marker;

SELECT 'TABLE_START:pre_wash_checklist' as marker;
SELECT * FROM pre_wash_checklist;
SELECT 'TABLE_END:pre_wash_checklist' as marker;

SELECT 'TABLE_START:promocode_service_packages' as marker;
SELECT * FROM promocode_service_packages;
SELECT 'TABLE_END:promocode_service_packages' as marker;

SELECT 'TABLE_START:promocodes' as marker;
SELECT * FROM promocodes;
SELECT 'TABLE_END:promocodes' as marker;

SELECT 'TABLE_START:push_notifications' as marker;
SELECT * FROM push_notifications;
SELECT 'TABLE_END:push_notifications' as marker;

SELECT 'TABLE_START:quick_bucks' as marker;
SELECT * FROM quick_bucks;
SELECT 'TABLE_END:quick_bucks' as marker;

SELECT 'TABLE_START:reviews' as marker;
SELECT * FROM reviews;
SELECT 'TABLE_END:reviews' as marker;

SELECT 'TABLE_START:role_permissions' as marker;
SELECT * FROM role_permissions;
SELECT 'TABLE_END:role_permissions' as marker;

SELECT 'TABLE_START:roles' as marker;
SELECT * FROM roles;
SELECT 'TABLE_END:roles' as marker;

SELECT 'TABLE_START:service_package_extra_service' as marker;
SELECT * FROM service_package_extra_service;
SELECT 'TABLE_END:service_package_extra_service' as marker;

SELECT 'TABLE_START:service_packages' as marker;
SELECT * FROM service_packages;
SELECT 'TABLE_END:service_packages' as marker;

SELECT 'TABLE_START:user_cards' as marker;
SELECT * FROM user_cards;
SELECT 'TABLE_END:user_cards' as marker;

SELECT 'TABLE_START:users' as marker;
SELECT * FROM users;
SELECT 'TABLE_END:users' as marker;
EOF

echo "Connecting to database and exporting all tables (this uses only 1 connection)..."
echo "Please enter password when prompted:"

# Export all data in one connection
mysql -h 127.0.0.1 -P 3307 -u QWS_QA -p qws_db < export_commands.sql > raw_export.txt

echo "Export complete! Now splitting into individual CSV files..."

# Split the raw export into individual CSV files
awk '
BEGIN { 
    current_file = ""
    in_table = 0
}
/^TABLE_START:/ { 
    if (current_file) close(current_file)
    gsub("TABLE_START:", "", $0)
    current_file = $0 ".csv"
    in_table = 1
    next
}
/^TABLE_END:/ { 
    in_table = 0
    next
}
in_table && !/^marker$/ { 
    if (current_file) print > current_file
}
' raw_export.txt

# Clean up temporary files
rm export_commands.sql
rm raw_export.txt

echo "Done! Check your directory for individual CSV files for each table."
echo "Files created:"
ls -1 *.csv | head -10
echo "... and more"