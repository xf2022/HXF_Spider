image_insert_sql = 'insert into hxf_spider.image (owner_id, owner_name, name, size, type, description, img_path, ' \
                   'thumnail_path, hash, exif, upload_date, create_time, update_time) values (%s, %s, %s, %s, %s, ' \
                   '%s, %s, %s, %s, %s, %s, %s, %s);'
image_del_by_id_sql = 'delete from hxf_spider.image where id=%s;'

verify_image_repeat_sql = 'select id, name, hash, img_path from hxf_spider.image where `hash` in %s;'
