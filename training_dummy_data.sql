
DROP TABLE IF EXISTS `dashboard_trainer`;

CREATE TABLE `dashboard_trainer` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `lastname` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `institution` varchar(9) COLLATE utf8_unicode_ci NOT NULL,
  `phone` varchar(17) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('1', 'Dayton', 'Balistreri', 'BENINCÀJU', '625.343.7704', 'ucarroll@example.org');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('2', 'Leanna', 'Bahringer', 'BENINCÀJU', '00181476339', 'alek22@example.com');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('3', 'Leonora', 'Barton', 'ATDA4', '1-590-020-6425x89', 'mlangworth@example.org');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('4', 'Adan', 'Ernser', 'BENINCÀJU', '864.640.7214x158', 'ygoldner@example.com');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('5', 'Leslie', 'Harvey', 'ATDA4', '(608)339-6498x206', 'schroeder.gaetano@example.org');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('6', 'Elmo', 'Lehner', 'BENINCÀJU', '1-532-390-0787x08', 'dibbert.gerry@example.net');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('7', 'Korey', 'Hoeger', 'ATDA4', '747.464.1987', 'vkerluke@example.net');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('8', 'Kirstin', 'Kirlin', 'ATDA4', '839-797-7754', 'cormier.iliana@example.org');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('9', 'Reuben', 'Cronin', 'BENINCÀJU', '07106883803', 'kris.wendell@example.com');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('10', 'Jaycee', 'Eichmann', 'BENINCÀJU', '(841)946-5006', 'feeney.dillan@example.org');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('11', 'Orlo', 'Fay', 'BENINCÀJU', '846.523.8683x6815', 'kessler.chauncey@example.com');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('12', 'Jonatan', 'Brown', 'ATDA4', '446.781.3446', 'qpowlowski@example.net');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('13', 'Carolina', 'Nienow', 'BENINCÀJU', '(263)897-6244x431', 'nsimonis@example.com');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('14', 'Estefania', 'Greenfelder', 'BENINCÀJU', '1-199-864-1993', 'wlueilwitz@example.com');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('15', 'Gabe', 'Schmidt', 'BENINCÀJU', '787-725-6404x0521', 'fbailey@example.org');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('16', 'Elvis', 'Koch', 'BENINCÀJU', '(822)377-9310x117', 'kmcclure@example.org');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('17', 'Nickolas', 'O\'Hara', 'ATDA4', '552-101-7995x9659', 'nwisoky@example.com');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('18', 'Ignatius', 'Harvey', 'BENINCÀJU', '1-646-625-2110x29', 'dietrich.dovie@example.org');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('19', 'Orie', 'Blick', 'ATDA4', '1-585-228-4741', 'dmoen@example.net');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('20', 'Polly', 'Dooley', 'BENINCÀJU', '418-153-4141x531', 'delphia.price@example.com');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('21', 'Cory', 'Cormier', 'BENINCÀJU', '667.157.3651x9043', 'jonathon11@example.net');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('22', 'Elvera', 'Homenick', 'ATDA4', '1-844-165-1089', 'brohan@example.net');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('23', 'Cicero', 'Dare', 'BENINCÀJU', '(077)559-6784x534', 'kenya13@example.com');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('24', 'Jeramy', 'Swaniawski', 'ATDA4', '(459)450-9213x102', 'ray.hane@example.net');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('25', 'Micah', 'Bradtke', 'BENINCÀJU', '1-883-030-5467x20', 'eleazar21@example.org');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('26', 'Darrion', 'Bayer', 'BENINCÀJU', '1-443-033-1710', 'eauer@example.com');
INSERT INTO `dashboard_trainer` (`id`, `firstname`, `lastname`, `institution`, `phone`, `email`) VALUES ('27', 'Glenda', 'Schulist', 'ATDA4', '(748)648-1996x658', 'andres24@example.net');


DROP TABLE IF EXISTS `dashboard_training`;

CREATE TABLE `dashboard_training` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `DateTime` datetime(6) NOT NULL,
  `longitude` double DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `number_of_participant` int(11) NOT NULL,
  `module_id_id` bigint(20) DEFAULT NULL,
  `trainer_id_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('1', '1974-06-17 04:09:16.000000', '10.75406832', '9.84240501', 68, '1', '1');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('2', '2009-03-17 08:03:16.000000', '11.05136275', '7.97495037', 13, '2', '2');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('3', '2021-12-10 01:13:31.000000', '10.80472231', '10.00757267', 9, '3', '3');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('4', '1983-11-16 11:55:54.000000', '8.43151374', '9.93621789', 2, '4', '4');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('5', '1995-11-11 10:18:29.000000', '10.50171292', '10.76139367', 74, '5', '5');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('6', '2000-05-13 22:45:58.000000', '9.6266884', '10.37621316', 87, '6', '6');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('7', '2020-09-01 12:18:10.000000', '9.74179763', '10.82637978', 51, '7', '7');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('8', '2010-09-09 17:12:10.000000', '8.11358543', '10.56573613', 50, '8', '8');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('9', '1976-12-13 20:41:32.000000', '8.07813544', '10.49448358', 84, '9', '9');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('10', '1981-04-02 19:42:29.000000', '9.2230728', '8.29401023', 72, '10', '10');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('11', '1990-10-25 03:07:51.000000', '9.4847474', '8.68387558', 67, '11', '11');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('12', '2009-07-17 08:12:50.000000', '8.46424062', '10.74551603', 1, '12', '12');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('13', '2006-07-23 04:04:11.000000', '10.11669079', '8.3673321', 68, '13', '13');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('14', '1991-12-28 05:24:06.000000', '11.08450805', '8.66825002', 54, '14', '14');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('15', '2000-11-18 15:28:01.000000', '8.20168959', '9.31976703', 27, '15', '15');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('16', '1976-02-13 23:49:58.000000', '9.57783834', '8.98279511', 42, '16', '16');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('17', '2007-06-13 12:11:31.000000', '10.80228496', '9.73929811', 58, '17', '17');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('18', '1970-09-01 06:20:57.000000', '10.90838201', '9.22719778', 19, '18', '18');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('19', '2016-01-08 04:56:55.000000', '8.38339358', '10.69484372', 72, '19', '19');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('20', '1993-12-22 14:35:07.000000', '8.95483142', '9.24524631', 8, '20', '20');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('21', '1990-11-02 07:22:03.000000', '8.04029358', '9.26292811', 67, '1', '21');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('22', '1998-10-19 00:36:20.000000', '10.31056257', '8.9670473', 52, '2', '22');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('23', '1981-01-11 13:32:58.000000', '9.11636871', '9.79190549', 27, '3', '23');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('24', '2002-08-31 21:52:36.000000', '9.01633159', '10.75256418', 56, '4', '24');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('25', '1986-05-01 01:05:41.000000', '9.27928008', '8.82554537', 6, '5', '25');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('26', '2006-12-14 21:47:36.000000', '10.79394605', '8.17885895', 16, '6', '26');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('27', '1989-11-02 21:19:13.000000', '9.71320768', '8.94753124', 32, '7', '27');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('28', '1986-09-06 20:23:47.000000', '8.30388213', '11.01136217', 79, '8', '28');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('29', '2021-07-30 04:47:00.000000', '8.32657593', '10.17670099', 35, '9', '29');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('30', '1984-09-06 08:13:07.000000', '9.42230999', '9.1452492', 7, '10', '30');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('31', '1996-08-30 00:34:49.000000', '10.1749686', '9.37139137', 70, '11', '1');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('32', '1983-02-17 20:03:20.000000', '9.44009199', '8.15257455', 67, '12', '2');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('33', '2000-09-23 20:48:21.000000', '8.46356159', '8.50316765', 25, '13', '3');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('34', '1977-11-14 11:01:34.000000', '9.61346303', '8.72565181', 14, '14', '4');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('35', '2020-11-30 11:11:35.000000', '10.57918752', '10.28144601', 51, '15', '5');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('36', '1990-03-24 05:44:54.000000', '10.29038498', '8.00333851', 90, '16', '6');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('37', '2001-06-10 14:41:02.000000', '10.27283399', '9.08432369', 64, '17', '7');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('38', '1971-03-10 18:22:30.000000', '10.37673663', '9.83071531', 88, '18', '8');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('39', '1972-10-11 22:14:13.000000', '10.43841499', '10.19432521', 68, '19', '9');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('40', '2006-04-08 09:43:39.000000', '9.60735856', '8.81747429', 78, '20', '10');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('41', '1977-02-26 16:40:22.000000', '8.69304228', '9.35441287', 59, '1', '11');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('42', '2002-11-17 13:46:36.000000', '10.34005745', '10.04223209', 35, '2', '12');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('43', '2019-06-04 14:17:07.000000', '9.0102684', '7.95073095', 28, '3', '13');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('44', '2016-05-26 18:47:45.000000', '9.31300719', '9.57065166', 56, '4', '14');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('45', '2011-08-05 23:34:32.000000', '9.25802833', '9.97377922', 27, '5', '15');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('46', '2009-03-14 11:13:40.000000', '10.3457274', '10.50641077', 71, '6', '16');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('47', '1997-08-22 16:28:53.000000', '8.26598623', '10.45676664', 81, '7', '17');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('48', '2007-06-05 15:48:32.000000', '9.9035069', '8.49925401', 22, '8', '18');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('49', '1985-08-22 13:23:02.000000', '10.63873361', '10.39832001', 73, '9', '19');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('50', '2011-04-18 12:40:34.000000', '9.22685669', '10.45161663', 8, '10', '20');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('51', '1998-09-21 19:18:37.000000', '8.75772519', '9.29174701', 31, '11', '21');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('52', '1993-08-19 05:37:50.000000', '10.97535674', '10.10463705', 43, '12', '22');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('53', '2017-05-02 15:11:49.000000', '10.01555374', '10.62883293', 27, '13', '23');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('54', '1972-08-16 19:18:12.000000', '8.46923621', '7.98330443', 56, '14', '24');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('55', '1980-09-09 22:15:47.000000', '9.0265226', '8.92265759', 57, '15', '25');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('56', '2016-02-03 05:46:02.000000', '10.05688465', '9.16476492', 10, '16', '26');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('57', '2015-09-12 07:54:54.000000', '8.4529118', '10.0474354', 20, '17', '27');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('58', '2007-06-26 01:18:13.000000', '10.7054418', '9.72094807', 88, '18', '28');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('59', '2014-07-27 08:16:03.000000', '9.04747544', '10.12231317', 51, '19', '29');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('60', '2007-12-26 18:55:41.000000', '10.26434806', '8.58994637', 80, '20', '30');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('61', '1996-11-10 22:11:01.000000', '10.55114915', '8.38983132', 25, '1', '1');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('62', '2011-07-15 07:38:38.000000', '11.01460996', '10.35405164', 55, '2', '2');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('63', '2003-10-25 11:28:26.000000', '10.72994942', '8.37561469', 80, '3', '3');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('64', '2003-05-08 09:51:11.000000', '10.46044222', '9.78069308', 64, '4', '4');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('65', '2012-05-27 23:12:59.000000', '10.30010383', '10.82691676', 76, '5', '5');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('66', '1988-05-09 02:39:03.000000', '8.50058356', '10.52075456', 61, '6', '6');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('67', '2016-04-16 17:23:42.000000', '9.02274782', '9.3486513', 89, '7', '7');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('68', '2007-09-26 11:24:29.000000', '8.56764289', '10.64868367', 15, '8', '8');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('69', '1971-06-29 03:24:08.000000', '10.84812569', '8.14593665', 12, '9', '9');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('70', '1974-12-25 05:22:41.000000', '8.96180792', '9.37157758', 87, '10', '10');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('71', '1998-11-28 04:32:03.000000', '9.19834856', '10.12773613', 59, '11', '11');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('72', '2002-07-30 18:23:13.000000', '10.91110167', '8.05285294', 50, '12', '12');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('73', '1987-01-05 05:48:29.000000', '8.8633016', '8.77387241', 85, '13', '13');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('74', '2015-12-27 09:56:03.000000', '10.0988671', '8.34072928', 60, '14', '14');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('75', '1990-12-15 15:55:54.000000', '10.95021809', '8.04203407', 61, '15', '15');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('76', '2002-02-25 17:33:16.000000', '10.89311524', '10.40150388', 48, '16', '16');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('77', '2011-10-11 10:00:57.000000', '9.51234504', '8.05034443', 87, '17', '17');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('78', '1997-02-07 17:16:23.000000', '8.01052927', '9.49538861', 12, '18', '18');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('79', '2013-03-10 05:29:17.000000', '10.41518356', '8.00156769', 85, '19', '19');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('80', '1983-01-05 08:02:11.000000', '8.71114776', '8.4800799', 75, '20', '20');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('81', '1985-12-16 05:20:24.000000', '8.98972237', '8.65640174', 45, '1', '21');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('82', '1988-12-23 22:09:11.000000', '8.75645492', '10.18906975', 83, '2', '22');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('83', '1979-08-31 06:47:20.000000', '7.92968055', '9.32783674', 57, '3', '23');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('84', '2007-02-26 10:51:54.000000', '10.18292717', '9.83769235', 1, '4', '24');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('85', '2017-01-21 04:31:28.000000', '9.63203366', '10.68912922', 29, '5', '25');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('86', '1979-01-31 13:33:18.000000', '10.56805378', '8.45399832', 2, '6', '26');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('87', '1971-08-08 20:29:19.000000', '8.75253861', '10.23469512', 33, '7', '27');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('88', '2003-12-29 22:43:44.000000', '9.89697862', '8.33127326', 73, '8', '28');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('89', '1986-04-28 20:44:35.000000', '10.56350955', '9.75848368', 64, '9', '29');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('90', '2016-04-10 20:37:54.000000', '8.01950777', '9.02242768', 32, '10', '30');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('91', '2015-03-10 21:54:20.000000', '7.93676128', '9.31669985', 50, '11', '1');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('92', '1988-04-22 23:16:21.000000', '9.53857907', '10.24697767', 12, '12', '2');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('93', '1982-03-11 14:56:48.000000', '9.48159848', '9.23310793', 23, '13', '3');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('94', '1974-03-11 18:17:30.000000', '9.47876011', '10.57780451', 72, '14', '4');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('95', '1987-09-27 13:21:43.000000', '8.32206519', '8.54031494', 33, '15', '5');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('96', '1971-11-26 19:46:59.000000', '8.31808869', '9.20535402', 81, '16', '6');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('97', '2018-12-11 12:49:00.000000', '11.00606729', '9.4214989', 72, '17', '7');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('98', '1982-04-03 21:13:53.000000', '8.81127104', '9.46517882', 35, '18', '8');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('99', '1981-06-06 14:05:20.000000', '8.63325809', '8.19835619', 34, '19', '9');
INSERT INTO `dashboard_training` (`id`, `DateTime`, `longitude`, `latitude`, `number_of_participant`, `module_id_id`, `trainer_id_id`) VALUES ('100', '2003-10-04 08:46:14.000000', '9.38486827', '8.13052258', 69, '20', '10');


#
# TABLE STRUCTURE FOR: dashboard_trainingmodule
#

DROP TABLE IF EXISTS `dashboard_trainingmodule`;

CREATE TABLE `dashboard_trainingmodule` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `module_name` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `category` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('1', 'porro', 'trucks');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('2', 'corrupti', 'room');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('3', 'in', 'apparel');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('4', 'voluptatem', 'visitor');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('5', 'laudantium', 'smile');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('6', 'voluptas', 'apparel');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('7', 'cumque', 'visitor');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('8', 'ut', 'coil');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('9', 'magni', 'building');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('10', 'deleniti', 'apparel');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('11', 'et', 'harmony');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('12', 'labore', 'fire');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('13', 'autem', 'smile');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('14', 'delectus', 'apparel');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('15', 'similique', 'trucks');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('16', 'ad', 'form');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('17', 'et', 'fire');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('18', 'quae', 'smile');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('19', 'quis', 'building');
INSERT INTO `dashboard_trainingmodule` (`id`, `module_name`, `category`) VALUES ('20', 'itaque', 'visitor');


