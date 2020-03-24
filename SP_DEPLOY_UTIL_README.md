# Deployment notes

## Notes when set up database

After run django migrate, you need to execute sql query for create some funtions, extentions or insert data.
You also should check them after restore database.

### Create is_json() funtion,that was used for create merchant report statistic,...

```
CREATE OR REPLACE FUNCTION is_json(varchar) RETURNS boolean AS $$
  DECLARE
    x json;
  BEGIN
    BEGIN
      x := $1;
    EXCEPTION WHEN others THEN
      RETURN FALSE;
    END;

    RETURN TRUE;
  END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

### Create funtion and extension for unaccent text .

```
create extension if not exists unaccent;
```

```
CREATE OR REPLACE FUNCTION vn_unaccent(text)
  RETURNS text AS
$func$
SELECT lower(translate($1,
'¹²³ÀÁẢẠÂẤẦẨẬẪÃÄÅÆàáảạâấầẩẫậãäåæĀāĂẮẰẲẴẶăắằẳẵặĄąÇçĆćĈĉĊċČčĎďĐđÈÉẸÊẾỀỄỆËèéẹêềếễệëĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨÌÍỈỊÎÏìíỉịîïĩĪīĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłÑñŃńŅņŇňŉŊŋÒÓỎỌÔỐỒỔỖỘỐỒỔỖỘƠỚỜỞỠỢÕÖòóỏọôốồổỗộơớờỡợởõöŌōŎŏŐőŒœØøŔŕŖŗŘřßŚśŜŝŞşŠšŢţŤťŦŧÙÚỦỤƯỪỨỬỮỰÛÜùúủụûưứừửữựüŨũŪūŬŭŮůŰűŲųŴŵÝýÿŶŷŸŹźŻżŽžёЁ',
'123AAAAAAAAAAAAAAaaaaaaaaaaaaaaAaAAAAAAaaaaaaAaCcCcCcCcCcDdDdEEEEEEEEEeeeeeeeeeEeEeEeEeEeGgGgGgGgHhHhIIIIIIIiiiiiiiIiIiIiIiIiJjKkkLlLlLlLlLlNnNnNnNnnNnOOOOOOOOOOOOOOOOOOOOOOOooooooooooooooooooOoOoOoEeOoRrRrRrSSsSsSsSsTtTtTtUUUUUUUUUUUUuuuuuuuuuuuuUuUuUuUuUuUuWwYyyYyYZzZzZzеЕ'));
$func$ LANGUAGE sql IMMUTABLE;
```

### Update document column of shop table after shop table has data or you restore database (because documents is json field,may be it wasn't backed up)

```
update shop
    set document=
        setweight(to_tsvector(coalesce(shop.code,'')), 'B') ||
        setweight(to_tsvector(vn_unaccent(coalesce( shop.address,''))), 'C') ||
        setweight(to_tsvector(coalesce(merchant.merchant_brand,'')), 'B')
        from merchant where merchant.id=merchant_id ;
```

### Run sql file to insert data into geodata table. This data was used for map visualize ,check latlng,... funtion.
file location
'''
sale_portal/geodata/management/sql_query/geojson_for_map.sql
'''