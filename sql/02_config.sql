-- Every threshold lives in one table, so a compliance officer can change a
-- rule with an UPDATE and re-run, with no code change.
DELETE FROM config;
INSERT INTO config VALUES ('band_low',        45000);
INSERT INTO config VALUES ('band_high',       49999.99);
INSERT INTO config VALUES ('struct_min_n',    4);
INSERT INTO config VALUES ('struct_min_total',180000);
INSERT INTO config VALUES ('pt_min_cr',       500000);
INSERT INTO config VALUES ('pt_ratio',        0.9);
INSERT INTO config VALUES ('fan_min_senders', 8);
INSERT INTO config VALUES ('fan_min_total',   100000);
INSERT INTO config VALUES ('fan_out_ratio',   0.7);
INSERT INTO config VALUES ('min_edge',        100000);
INSERT INTO config VALUES ('cyc_min_ratio',   0.8);
INSERT INTO config VALUES ('inc_mult',        10);
INSERT INTO config VALUES ('inc_min_cr',      100000);
INSERT INTO config VALUES ('business_mult',   10);
INSERT INTO config VALUES ('flag_score',      40);
INSERT INTO config VALUES ('ctr_single',      1000000);

DELETE FROM typology_weights;
INSERT INTO typology_weights VALUES ('STRUCTURING',    50);
INSERT INTO typology_weights VALUES ('CIRCULAR',       50);
INSERT INTO typology_weights VALUES ('PASSTHROUGH',    40);
INSERT INTO typology_weights VALUES ('FANIN_MULE',     40);
INSERT INTO typology_weights VALUES ('INCOME_MISMATCH',30)
