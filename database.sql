-- schema.sql

drop database if exists portrait;

create database portrait;

use portrait;

-- grant select, insert, update, delete on awesome.* to 'www-data'@'localhost' identified by 'www-data';

create table xiuren_album (
    `id` int not null AUTO_INCREMENT,
    `title` varchar(500) not null,
    `digest` varchar(500) null,
    `description` varchar(2048) null,
    `category_id` int not null,
    `tags` varchar(100) null,
    `cover` varchar(200) null,
    `cover_backup` varchar(200) null,
    `author` varchar(100) null,
    `view_count` int unsigned not null default 0,
    `origin_link` varchar(200) null,
    `origin_created_at` real not null,
    `created_at` real not null,
    `updated_at` real not null,
    `is_enabled` bool not null default 1,
    unique key `idx_title` (`title`),
    unique key `idx_origin_link` (`origin_link`),
    key `idx_origin_created_at` (`origin_created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- alter table xiuren_album change cagetory_id category_id int;
-- alter table xiuren_album add column `cover_backup` varchar(200) null after `cover`;

create table xiuren_images (
    `id` int not null AUTO_INCREMENT,
    `album_id` int not null,
    `image_url` varchar(200) not null,
    `backup_url` varchar(200) null,
    `created_at` real not null,
    `updated_at` real not null,
    `is_enabled` bool not null default 1,
    -- unique key `idx_image_url` (`image_url`),
    key `idx_album_id` (`album_id`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- alter table xiuren_images add column `backup_url` varchar(200) null after `image_url`;

create table xiuren_categories (
    `id` int not null AUTO_INCREMENT,
    `name` varchar(100) not null,
    `title` varchar(100) not null,
    `created_at` real not null,
    `updated_at` real not null,
    `is_enabled` bool not null default 1,
    unique key `idx_name` (`name`),
    unique key `idx_title` (`title`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;

create table xiuren_tags (
    `id` int not null AUTO_INCREMENT,
    `title` varchar(100) not null,
    `created_at` real not null,
    `updated_at` real not null,
    `is_enabled` bool not null default 1,
    unique key `idx_title` (`title`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8mb4 COLLATE=utf8mb4_unicode_ci;
