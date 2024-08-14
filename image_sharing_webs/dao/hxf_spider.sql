create database if not exists `hxf_spider`;
use `hxf_spider`;
--  tsak
-- id
-- name
-- web_id
-- web_name
-- description
-- create_time
-- update_time
drop table if exists task;
create table if not exists `task` (
	id int not null AUTO_INCREMENT comment '唯一标识',
	`name` varchar(64) not null comment '任务名',
	web_id int not null comment '目标网站ID',
	web_name varchar(32) comment '目标网站名称',
	description varchar(128) comment '详情',
	create_time datetime comment '创建时间',
	update_time datetime comment '更新时间',
	primary key (`id`),
	unique key (name)

)engine=Innodb default charset=utf8mb4;

-- task_config
-- id
-- task_id
-- handle
-- description
-- create_time
-- update_time
drop table if exists task_config;
create table if not exists `task_config` (
	id int not null AUTO_INCREMENT comment '唯一标识',
	task_id int not null,
	task_name varchar(64) not null,
	handle varchar(128) not null comment '执行程序',
	description varchar(128),
	create_time datetime comment '创建时间',
	update_time datetime comment '更新时间',
	primary key (`id`),
	unique key (task_id)

)engine=Innodb default charset=utf8mb4;

-- task_schedule
-- id
-- task_id
-- plan_type
-- plan_date
-- plan_time
-- is_normal
-- last_start_time
-- last_end_time
-- last_status
-- create_time
-- update_time
drop table if exists task_schedule;
create table if not exists task_schedule(
	id int not null AUTO_INCREMENT,
	task_id int not null,
	task_name varchar(64) not null,
	plan varchar(16) not null,
	plan_date varchar(16),
	plan_time varchar(16),
	is_normal boolean default true,
	last_start_time datetime comment '上次执行时间',
	last_status smallint comment '上次任务执行的状态',
	last_end_time datetime comment '上次结束时间',
	create_time datetime comment '创建时间',
	update_time datetime comment '更新时间',
	primary key (`id`),
	unique key (task_id)

)engine=Innodb default charset=utf8mb4;

-- task_record
-- id
-- business_date
-- status
-- exec_log
-- create_time
-- update_time
drop table if exists task_record;
create table if not exists task_record(
	id int not null AUTO_INCREMENT,
	task_id int not null,
	task_name varchar(64) not null,
	bussiness_date date comment '执行日期',
	status smallint comment '任务状态',
	exec_log varchar(128) comment '执行日志',
	create_time datetime comment '创建时间',
	update_time datetime comment '更新时间',
	primary key (id),
	unique key (task_id, bussiness_date)

)engine=Innodb default charset=utf8mb4;

-- image
-- id int
-- owner_id int
-- owner varchar
-- name varchar
-- size varchar
-- type varchar
-- description varchar
-- img_path varchar
-- thumnail_path varchar
-- hash varchar
-- exif varchar
-- tags varchar
-- create_time datetime
-- update_time datetime
drop table if exists image;
create table if not exists image(
	id int not null AUTO_INCREMENT,
	owner_id int comment '来源ID',
	owner_name varchar(32),
	name varchar(128) not null comment '图片名称',
	`size` varchar(32) not null comment '图片尺寸',
	`type` varchar(8) not null comment '图片类型',
	description varchar(128) not null comment '图片描述',
	img_path varchar(128) not null comment '图片地址',
	thumnail_path varchar(128) comment '缩略图地址',
	hash varchar(256) comment '哈希值',
	exif varchar(128) comment '拍摄信息',
	upload_date date comment '上传日期',
	create_time datetime comment '创建时间',
	update_time datetime comment '更新时间',
	primary key (`id`),
	unique key (hash),
	unique key (owner_id, name)

)engine=Innodb default charset=utf8mb4;

-- target_website
-- id
-- name
-- url
-- description
-- config
-- create_time
-- update_time
drop table if exists target_website;
create table if not exists target_website(
	id int not null AUTO_INCREMENT,
	name varchar(32) not null,
	url varchar(64) not null comment '网址',
	description varchar(128) comment '网站描述',
	config varchar(128),
	create_time datetime comment '创建时间',
	update_time datetime comment '更新时间',
	primary key (`id`),
	unique key(name, url)

)engine=Innodb default charset=utf8mb4;

-- account
-- id
-- web_id
-- web_name
-- name
-- password
-- cookies
-- create_time
-- update_time
drop table if exists account;
create table if not exists account (
	id int not null AUTO_INCREMENT,
	web_id int not null comment '网站ID',
	web_name varchar(32) not null,
	name varchar(32) not null comment '账号名',
	`password` varchar(32) not null comment '密码',
	cookies varchar(512) comment '登录cookie',
	create_time datetime comment '创建时间',
	update_time datetime comment '更新时间',
	primary key (id),
	unique key (web_id, name, `password`)

)engine=Innodb default charset=utf8mb4;

-- image_sharing --



