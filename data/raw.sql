-- name: create!
CREATE TABLE IF NOT EXISTS id_path (
    id       INTEGER       PRIMARY KEY,
    src      TEXT          NOT NULL UNIQUE,
    raw      TEXT          NOT NULL
);
CREATE TABLE IF NOT EXISTS file_type (
    id       INTEGER       PRIMARY KEY REFERENCES id_path(id),
    type     TEXT          
);
CREATE TABLE IF NOT EXISTS no_care_file (
    path     TEXT          PRIMARY KEY
);

-- name: insert_id_path_rows*!
insert into id_path values (:id, :src, :raw);
-- name: insert_no_care_files*!
insert into no_care_file values (:path);
-- name: insert_file_types*!
insert into file_type values (:id, :type);

-- name: insert_id_path_row!
insert into id_path values (:id, :src, :raw);
-- name: insert_no_care_file!
insert into no_care_file values (:path);
-- name: insert_file_type!
insert into file_type values (:id, :type);

-- name: id_path
select * from id_path;
-- name: src_raw
select src, raw from id_path;
-- name: max_id$
select max(id) from id_path;
