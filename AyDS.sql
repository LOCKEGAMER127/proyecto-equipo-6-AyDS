DROP DATABASE IF EXISTS AyDS;
CREATE DATABASE AyDS
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE AyDS;

-- ==========================
-- ROLES
-- ==========================
CREATE TABLE roles(
    idroles INT AUTO_INCREMENT,
    nombre VARCHAR(20) NOT NULL UNIQUE,
    PRIMARY KEY(idroles)
);
INSERT INTO roles (nombre) 
VALUES ('Alumno'),('Administrador');

-- ==========================
-- PREGUNTAS DE RECUPERACIÓN
-- ==========================
CREATE TABLE preguntas_recuperacion(
    idrecuperacion INT AUTO_INCREMENT,
    pregunta VARCHAR(45) NOT NULL,
    PRIMARY KEY(idrecuperacion)
);

INSERT INTO preguntas_recuperacion(pregunta)
VALUES ('En dónde naciste?'), ('Nombre de tu personaje favorito?'), ('Nombre de tu primera mascota?'), ('Nombre de tu mejor amigo?'), ('Comida favorita?');


-- ==========================
-- USUARIO
-- ==========================
CREATE TABLE usuario(
    boleta INT NOT NULL,
    nombre VARCHAR(45) NOT NULL,
    contraseña VARCHAR(256) NOT NULL,
    res_recu VARCHAR(256) NOT NULL,
    roles_idroles INT NOT NULL,
    preguntas_recuperacion_idrecuperacion INT NOT NULL,

    PRIMARY KEY (boleta),

    CONSTRAINT fk_usuario_roles
    FOREIGN KEY (roles_idroles)
    REFERENCES roles(idroles),

    CONSTRAINT fk_usuario_preguntas
    FOREIGN KEY (preguntas_recuperacion_idrecuperacion)
    REFERENCES preguntas_recuperacion(idrecuperacion)
);

-- ==========================
-- DOCENTE
-- ==========================
CREATE TABLE docente(
    iddocente INT AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    inf INT NOT NULL,
    usuario_boleta INT NOT NULL,

    PRIMARY KEY (iddocente),

    CONSTRAINT fk_docente_usuario
    FOREIGN KEY (usuario_boleta)
    REFERENCES usuario(boleta)
);

-- ==========================
-- MATERIAS
-- ==========================
CREATE TABLE materias(
    idmaterias INT AUTO_INCREMENT,
    nombre VARCHAR(45) NOT NULL,
    estres INT NOT NULL,
    docente_iddocente INT NOT NULL,
    usuario_boleta INT NOT NULL,

    PRIMARY KEY(idmaterias),

    CONSTRAINT fk_materias_docente
    FOREIGN KEY(docente_iddocente)
    REFERENCES docente(iddocente),

    CONSTRAINT fk_materias_usuario
    FOREIGN KEY(usuario_boleta)
    REFERENCES usuario(boleta)
);

-- ==========================
-- DATOS USUARIO TEMP
-- ==========================
CREATE TABLE datos_usuario_temp(
    usuario_boleta INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    grupo VARCHAR(45) NOT NULL,
    sit_acad VARCHAR(45) NOT NULL,
    num_materias INT NOT NULL,
    semestre INT NOT NULL,
    str_tolerancia VARCHAR(45) NOT NULL,
    perse_carga INT NOT NULL,

    PRIMARY KEY(usuario_boleta,fecha_inicio),

    CONSTRAINT fk_temp_usuario
    FOREIGN KEY(usuario_boleta)
    REFERENCES usuario(boleta)
);

-- ==========================
-- QUIZ BASE
-- ==========================
CREATE TABLE quiz_base(
    usuario_boleta INT NOT NULL,
    fecha_quiz DATE NOT NULL,
    grupo VARCHAR(45) NOT NULL,
    sit_acad VARCHAR(45) NOT NULL,
    semestre INT NOT NULL,
    str_tolerancia INT NOT NULL,
    perse_carga INT NOT NULL,
    grupo_relacion INT NOT NULL,
    pers_anim_general INT NOT NULL,
    motivacion_acad INT NOT NULL,
    persepcion_academica INT NOT NULL,
    hobbies INT NOT NULL,

    PRIMARY KEY(usuario_boleta,fecha_quiz),

    CONSTRAINT fk_quiz_usuario
    FOREIGN KEY(usuario_boleta)
    REFERENCES usuario(boleta)
);

-- ==========================
-- ACTIVIDADES
-- ==========================
CREATE TABLE actividades(
    id_actividad INT AUTO_INCREMENT,
    usuario_boleta INT NOT NULL,
    materias_idmaterias INT,
    dia DATE NOT NULL,
    tiempo_estimado VARCHAR(45) NOT NULL,
    estres_generado INT NOT NULL,
    estado TINYINT NOT NULL DEFAULT 0,
    descripcion VARCHAR(45) NOT NULL,
    tiempo_real INT,

    PRIMARY KEY(id_actividad),

    CONSTRAINT fk_actividad_usuario
    FOREIGN KEY(usuario_boleta)
    REFERENCES usuario(boleta),

    CONSTRAINT fk_actividad_materia
    FOREIGN KEY(materias_idmaterias)
    REFERENCES materias(idmaterias)
);