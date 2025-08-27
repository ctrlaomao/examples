-- 参数配置数据库表结构设计
-- 基于新建参数配置界面字段分析

-- 1. 主参数配置表
CREATE TABLE `parameter_config` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `config_name` VARCHAR(100) NOT NULL COMMENT '配置名称',
    `config_description` TEXT COMMENT '配置描述',
    
    -- ROI相关配置
    `roi_optimization_threshold` DECIMAL(10,4) DEFAULT 0.2000 COMMENT '优化窗法标ROI阈值',
    `roi_optimization_coefficient` INT DEFAULT 2 COMMENT '优化窗法综合系数',
    `roi_legal_threshold` DECIMAL(10,4) DEFAULT 0.4000 COMMENT '优化窗合法ROI阈值',
    `roi_legal_coefficient` INT DEFAULT 1 COMMENT '优化窗合法系数',
    `optimization_quality_ratio` DECIMAL(5,4) DEFAULT 0.1000 COMMENT '优化窗质效比例(%)',
    
    -- 代投相关配置
    `agency_coefficient` DECIMAL(5,4) DEFAULT 0.8000 COMMENT '代投系数',
    
    -- 设计师相关配置
    `designer_material_ratio` DECIMAL(5,4) DEFAULT 0.1700 COMMENT '设计师表材质效比例(%)',
    `designer_outsource_coefficient` INT DEFAULT 10 COMMENT '设计师表材外包系数',
    
    -- 系统字段
    `status` TINYINT DEFAULT 1 COMMENT '状态(0:禁用 1:启用)',
    `created_by` BIGINT UNSIGNED COMMENT '创建人ID',
    `updated_by` BIGINT UNSIGNED COMMENT '更新人ID',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at` TIMESTAMP NULL DEFAULT NULL COMMENT '删除时间',
    
    PRIMARY KEY (`id`),
    KEY `idx_config_name` (`config_name`),
    KEY `idx_status` (`status`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='参数配置主表';

-- 2. ROI系数配置表（第37日达标roi系数）
CREATE TABLE `roi_coefficient_config` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `config_id` BIGINT UNSIGNED NOT NULL COMMENT '参数配置ID',
    `coefficient_type` VARCHAR(50) NOT NULL COMMENT '系数类型(巨量微小,广点通微小,快手微小,BM微小,巨量抖小,巨量OSAPP,巨量安卓app,ASA,taptap)',
    `coefficient_value` DECIMAL(5,2) NOT NULL COMMENT '系数值',
    `unit` VARCHAR(10) DEFAULT '%' COMMENT '单位',
    `sort_order` INT DEFAULT 0 COMMENT '排序',
    
    -- 系统字段
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (`id`),
    KEY `idx_config_id` (`config_id`),
    KEY `idx_coefficient_type` (`coefficient_type`),
    FOREIGN KEY (`config_id`) REFERENCES `parameter_config`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='ROI系数配置表';

-- 3. 特殊渠道配置表
CREATE TABLE `special_channel_config` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `config_id` BIGINT UNSIGNED NOT NULL COMMENT '参数配置ID',
    `channel_name` VARCHAR(100) NOT NULL COMMENT '渠道名称',
    `channel_coefficient` INT NOT NULL COMMENT '渠道系数',
    `sort_order` INT DEFAULT 0 COMMENT '排序',
    
    -- 系统字段
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (`id`),
    KEY `idx_config_id` (`config_id`),
    KEY `idx_channel_name` (`channel_name`),
    FOREIGN KEY (`config_id`) REFERENCES `parameter_config`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='特殊渠道配置表';

-- 4. 代投配置表
CREATE TABLE `agency_config` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `config_id` BIGINT UNSIGNED NOT NULL COMMENT '参数配置ID',
    `agency_code` VARCHAR(20) NOT NULL COMMENT '代投编号',
    `agency_name` VARCHAR(100) NOT NULL COMMENT '代投名称',
    `sort_order` INT DEFAULT 0 COMMENT '排序',
    
    -- 系统字段
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (`id`),
    KEY `idx_config_id` (`config_id`),
    KEY `idx_agency_code` (`agency_code`),
    FOREIGN KEY (`config_id`) REFERENCES `parameter_config`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代投配置表';

-- 5. 插入示例数据
INSERT INTO `parameter_config` (
    `config_name`, 
    `config_description`,
    `roi_optimization_threshold`,
    `roi_optimization_coefficient`,
    `roi_legal_threshold`,
    `roi_legal_coefficient`,
    `optimization_quality_ratio`,
    `agency_coefficient`,
    `designer_material_ratio`,
    `designer_outsource_coefficient`,
    `created_by`
) VALUES (
    '默认参数配置',
    '系统默认的参数配置方案',
    0.2000,
    2,
    0.4000,
    1,
    0.1000,
    0.8000,
    0.1700,
    10,
    1
);

-- 插入ROI系数配置示例数据
INSERT INTO `roi_coefficient_config` (`config_id`, `coefficient_type`, `coefficient_value`, `sort_order`) VALUES
(1, '巨量微小', 38.5, 1),
(1, '广点通微小', 26.6, 2),
(1, '快手微小', 38.5, 3),
(1, 'BM微小', 35.7, 4),
(1, '巨量抖小', 38.0, 5),
(1, '巨量OSAPP', 30.6, 6),
(1, '巨量安卓app', 32.6, 7),
(1, 'ASA', 37.6, 8),
(1, 'taptap', 40.8, 9);

-- 插入特殊渠道配置示例数据
INSERT INTO `special_channel_config` (`config_id`, `channel_name`, `channel_coefficient`, `sort_order`) VALUES
(1, '广点通微小', 2, 1),
(1, '快手微小', 3, 2);

-- 插入代投配置示例数据
INSERT INTO `agency_config` (`config_id`, `agency_code`, `agency_name`, `sort_order`) VALUES
(1, '01', '请输入', 1);