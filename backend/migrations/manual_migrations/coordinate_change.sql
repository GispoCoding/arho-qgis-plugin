create or replace procedure change_srid(relation name, srid int) language plpgsql AS
$$
DECLARE
    view_def text;
    geom_type text;
BEGIN
    view_def = pg_get_viewdef(('hame.'||relation||'_v')::regclass::oid, true);
    EXECUTE format('DROP VIEW hame.%I', relation||'_v');
    SELECT "type" INTO geom_type FROM geometry_columns WHERE f_table_schema = 'hame' and f_table_name = relation;
    EXECUTE format('ALTER TABLE hame.%I ALTER COLUMN geom TYPE geometry(%s, %s) USING st_transform(geom, %s)', relation, geom_type, srid, srid);
    EXECUTE format('CREATE VIEW hame.%I AS %s', relation||'_v', view_def);
    EXECUTE format('GRANT SELECT ON hame.%I TO arho_read_only', relation||'_v');
    EXECUTE format('GRANT SELECT, DELETE, UPDATE, INSERT ON hame.%I TO arho_read_write',  relation||'_v');
    EXECUTE format('CREATE TRIGGER %I
        INSTEAD OF INSERT OR DELETE OR UPDATE
        ON hame.%I
        FOR EACH ROW
        EXECUTE FUNCTION hame.trgf_iiud()
        ', 'trg_iiud_'||relation||'_v', relation||'_v');
END
$$;

call change_srid('point', 3879);
call change_srid('land_use_area', 3879);
call change_srid('other_area', 3879);
call change_srid('line', 3879);
ALTER TABLE hame.plan ALTER COLUMN geom TYPE geometry(multipolygon, 3879) USING st_transform(geom, 3879);

drop procedure change_srid(name, int);
