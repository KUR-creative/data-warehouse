-- name: create!
CREATE TABLE IF NOT EXISTS id_path (
    id       INTEGER       PRIMARY KEY,
    src      TEXT          NOT NULL UNIQUE,
    raw      TEXT          NOT NULL
);
CREATE TABLE IF NOT EXISTS file_type (
    id       INTEGER       PRIMARY KEY REFERENCES id_path(id),
    type     TEXT          NOT NULL
);
CREATE TABLE IF NOT EXISTS mask ( --- mask generated from id
    id       INTEGER       PRIMARY KEY REFERENCES id_path(id),
    path     TEXT          NOT NULL,
    type     TEXT          NOT NULL  --- rgb, v0, ...
);
CREATE TABLE IF NOT EXISTS image ( --- image generated from id
    id       INTEGER       PRIMARY KEY REFERENCES id_path(id),
    path     TEXT          NOT NULL,
    type     TEXT          NOT NULL  --- rmtxt-v0, ...
);
CREATE TABLE IF NOT EXISTS no_care_file (
    path     TEXT          PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS shape ( --- image generated from id
    id       INTEGER       NOT NULL REFERENCES id_path(id),
    type     TEXT          NOT NULL,  --- rmtxt-v0, ...
    height   INTEGER       NOT NULL CHECK(0 < height),
    width    INTEGER       NOT NULL CHECK(0 < width),
    depth    INTEGER       NOT NULL CHECK(0 < depth),
    PRIMARY KEY(id, type)
);

---------------------------------------------------------------
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
-- name: insert_mask!
insert into mask values(:id, :path, :type);
-- name: insert_image!
insert into image values(:id, :path, :type);

---------------------------------------------------------------
-- name: id_path
select * from id_path;
-- name: src_raw
select src, raw from id_path;
-- name: max_id$
select max(id) from id_path;

-- name: rmtxt_mask_paths_shuffled
SELECT mask.path, image.path
FROM   mask JOIN image ON mask.id = image.id
WHERE  mask.type = :mask_type
  AND  image.type = :image_type
ORDER  BY Random();

-- name: unknown_file_type_raws
select id_path.id, raw from id_path
left join file_type on id_path.id = file_type.id
where file_type.id is NULL order by id_path.id;

-- name: random_raws_without_mask_or_img
SELECT raw 
FROM   id_path 
       LEFT OUTER JOIN (SELECT id 
                        FROM   mask 
                        UNION 
                        SELECT id 
                        FROM   image) AS done 
                    ON id_path.id = done.id 
       JOIN file_type 
         ON id_path.id = file_type.id 
WHERE  done.id IS NULL 
       AND ( file_type.type = 'image/jpeg' 
              OR file_type.type = 'image/png' ) 
ORDER  BY Random(); 
