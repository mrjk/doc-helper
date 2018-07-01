#!/bin/bash
#
# This scripts helps to manipulate Openstack databases.
#
#
# # Notes:
# 
# Here some notes:
# - To delete a server, please try with `server_delete` first, and follow instructions
#   then use `server_force_delete` in last case.
#
#
# # Informations
# 
# - Version: 0.1-beta
# - Authors: rcordier
# - Date: 07/06/2018
# - License: Ubisoft
#
#
# EOF_DOC


set -euo pipefail

scr_help()
{
    echo "Usage: $0 server_show ID"
    echo "       $0 server_delete ID COMPUTE|AUTO"
    echo "       $0 server_force_delete ID"
    echo
    echo "Commands:"
    echo "  server_show           : Show nova entry"
    echo "  server_delete         : Fix 'openstack server delete \$srv' command for an instance (clean)"
    echo "                          Omit the COMPUTE field to get a list of 10 computes, or use AUTO to"
    echo "                          automagically select it (need testing)"
    echo "  server_force_delete   : Fix 'openstack server delete \$srv' command for an instance (dirty)"
}

scr_server_show ()
{
    local instance_id=$1

    # Fields
    local fields1="uuid, project_id, hostname, host, os_type, created_at, task_state, vm_state"
    local fields2="key_name, deleted_at, deleted"
    local fields="$fields1, $fields2"
    #local fields="*"

    echo "INFO: Instance '$instance_id' data" 
    mysql nova -e "select $fields from instances where uuid = '$instance_id'\G"

}

scr_server_force_delete ()
{
    local instance_id=$1

    # This should be safe especially with bash strict mode
    mysql nova -e "update instances set deleted='1', vm_state='deleted', deleted_at=now() where uuid = '$instance_id';"
    echo "INFO: Instance '$instance_id' cleaned" 
    

}

scr_server_delete ()
{
    local instance_id=$1
    local dest=${2:-NONE}

    # User helper, comment this block to automagically select the 1st available
    if [ "$dest" == "NONE" ]; then
      echo "ERR: You need to provide a destination node, like those:"
      mysql nova -e "select host from compute_nodes where deleted = 0 and updated_at < DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 5 minute ) limit 10"
      exit 1
    fi

    if [ "$dest" == "AUTO" ]; then
      # Automagically check one
      valid_host=$(mysql nova -N -B -e "select host from compute_nodes where deleted = 0 and updated_at < DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 5 minute ) limit 1")
    else

      # Check if destination exists
      check_host=$(mysql nova -N -B -e "select host from compute_nodes where uuid = '$dest' deleted = 0 and updated_at < DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 5 minute ) limit 1")

      # Fail if not
      [ -n "$check_host" ] || {
        echo "ERR: Destination node '$dest' is not valid, please"
        exit 1
      }

      valid_host=$dest

    fi
    
    # Move the instance
    mysql nova -e "update instances set host='$valid_host',node='$valid_host' where uuid='$instance_id'"

    # Informations
    echo "INFO: Instance '$instance_id' has been moved to '$valid_host'" 
    echo "INFO: Please run 'openstack server delete $instance_id'"

}



scr_menu_main ()
{
  #set -x
  local word=${1:-help}
  shift 1 || true

  # Starting real things
  case $word in

    # First level words
    server_show)
      scr_server_show $@
      ;;
    server_force_delete)
      scr_server_force_delete $@
      ;;
    server_delete)
      scr_server_delete $@
      ;;
    help|-h|--help)
      scr_help
      ;;
    *)
      scr_help
      return 1
      ;;
  esac

}
        
scr_menu_main ${@:-}

