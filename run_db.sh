docker run \
    -e MYSQL_ROOT_PASSWORD=root  \
    -e MYSQL_USER=rbacpoc  \
    -e MYSQL_PASSWORD=rbacpoc  \
    -e MYSQL_DATABASE=rbacpoc  \
    -e MYSQL_MASTER_PORT_NUMBER=3306  \
    -e MYSQL_AUTHENTICATION_PLUGIN=mysql_native_password  \
    -p 3306:3306 \
    --name rbac-mysql-db -d \
    bitnami/mysql:latest