;;; ШАБЛОНЫ ФАКТОВ
;; Факт для хранения интересов пользователя
(deftemplate interest
    (slot name (type SYMBOL) (allowed-symbols математика программирование дизайн управление экономика))
    (slot value (type SYMBOL) (allowed-symbols да нет)))

;; Факт для хранения мышления
(deftemplate thinking
    (slot name (type SYMBOL) (allowed-symbols алгоритмическое аналитическое творческое))
    (slot value (type SYMBOL) (allowed-symbols да нет усилено)))

;; Факт для хранения финансовой грамотности
(deftemplate financial-literacy
    (slot value (type SYMBOL) (allowed-symbols да нет усилено)))

;; Факт для хранения специализаций
(deftemplate specialization
    (slot name (type SYMBOL) (allowed-symbols разработка-ИИ веб-разработка дизайн-интерьеров управление-проектами бизнес-аналитика))
    (slot value (type SYMBOL) (allowed-symbols да нет альтернативный-путь альтернативный-путь-к-компьютерным-наукам)))

;; Факт для хранения результатов (факультетов)
(deftemplate faculty
    (slot name (type SYMBOL) (allowed-symbols компьютерных-наук дизайна искусств государственного-управления муниципального-управления другой-университет))
    (slot value (type SYMBOL) (allowed-symbols да нет)))

;; Факт для хранения итогового результата
(deftemplate result
    (slot value (type STRING)))

;; Целочисленные факты (по требованию задания)
(deftemplate student-age
    (slot value (type INTEGER) (range 16 30)))

(deftemplate student-grade
    (slot value (type INTEGER) (range 1 5)))

(deftemplate student-id
    (slot value (type INTEGER)))

;; Факт для отслеживания состояния системы
(deftemplate system-state
    (slot phase (type SYMBOL) (allowed-symbols начальная инициализация ввод-данных обработка вывод-результата)))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; ФУНКЦИИ
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Функция для запроса ввода да/нет
(deffunction ask-yes-no (?question)
    (printout t ?question " (да/нет): ")
    (bind ?answer (lowcase (read)))
    (while (and (neq ?answer да) (neq ?answer нет)) do
        (printout t "Пожалуйста, введите 'да' или 'нет': ")
        (bind ?answer (lowcase (read))))
    ?answer)

;; Функция для запроса целого числа
(deffunction ask-integer (?question ?min ?max)
    (printout t ?question " (" ?min "-" ?max "): ")
    (bind ?answer (read))
    (while (or (not (integerp ?answer)) (< ?answer ?min) (> ?answer ?max)) do
        (printout t "Пожалуйста, введите целое число от " ?min " до " ?max ": ")
        (bind ?answer (read)))
    ?answer)

;; Функция для проверки всех интересов
(deffunction all-interests-no ()
    (bind ?count 0)
    (do-for-all-facts ((?f interest)) TRUE
        (if (eq ?f:value нет) then
            (bind ?count (+ ?count 1))))
    (if (eq ?count 5) then TRUE else FALSE))

;; Функция для вывода итогового результата
(deffunction print-result ()
    (printout t crlf "============== РЕЗУЛЬТАТ ==============" crlf)
    (do-for-all-facts ((?r result)) TRUE
        (printout t "Рекомендуется: " ?r:value crlf))
    (printout t "========================================" crlf))

;; Функция для сброса системы (для тестирования)
(deffunction reset-system ()
    (retract *)
    (assert (system-state (phase начальная))))

;; Функция для получения случайного числа в диапазоне
(deffunction random-between (?min ?max)
    (bind ?range (+ (- ?max ?min) 1))
    (+ ?min (integer (* (random) ?range))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; ПРАВИЛА
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Правило 0: Инициализация системы
(defrule init-system
    ?state <- (system-state (phase начальная))
    =>
    (retract ?state)
    (assert (system-state (phase инициализация)))
    (printout t "=========== СИСТЕМА ВЫБОРА ФАКУЛЬТЕТА ===========" crlf)
    (printout t "Ответьте на вопросы для определения подходящего факультета." crlf crlf))

;; Правило 1: Инициализация целочисленных фактов
(defrule init-integer-facts
    ?state <- (system-state (phase инициализация))
    =>
    (retract ?state)
    (assert (system-state (phase ввод-данных)))
    ;; Генерация уникального ID студента
    (assert (student-id (value (random-between 1000 9999))))
    ;; Установка возраста по умолчанию (можно изменить на интерактивный ввод)
    (assert (student-age (value 18)))
    ;; Установка среднего балла по умолчанию
    (assert (student-grade (value 4)))
    ;; Получение ID студента для вывода
    (bind ?id-facts (find-all-facts ((?f student-id)) TRUE))
    (if (> (length$ ?id-facts) 0) then
        (bind ?id-fact (nth$ 1 ?id-facts))
        (printout t "ID студента: " (fact-slot-value ?id-fact value) crlf))
    (printout t "Возраст: 18 лет (по умолчанию)" crlf)
    (printout t "Средний балл: 4 (по умолчанию)" crlf crlf))

;; Правило 2: Запрос интересов
(defrule ask-interests
    ?state <- (system-state (phase ввод-данных))
    =>
    (retract ?state)
    (assert (system-state (phase обработка)))
    ;; Запрос всех интересов
    (assert (interest (name математика) (value (ask-yes-no "Есть ли у вас интерес к математике?"))))
    (assert (interest (name программирование) (value (ask-yes-no "Есть ли у вас интерес к программированию?"))))
    (assert (interest (name дизайн) (value (ask-yes-no "Есть ли у вас интерес к дизайну?"))))
    (assert (interest (name управление) (value (ask-yes-no "Есть ли у вас интерес к управлению?"))))
    (assert (interest (name экономика) (value (ask-yes-no "Есть ли у вас интерес к экономике?"))))
    (printout t crlf "Спасибо! Обрабатываю ваши ответы..." crlf crlf))
	
;; Правило 3: Проверка отсутствия интересов
(defrule no-interests
    (system-state (phase обработка))
    (student-age (value ?age))
    (student-grade (value ?grade))
    (test (all-interests-no))
    =>
    (assert (result (value "Выберите другой университет")))
    (assert (faculty (name другой-университет) (value да)))
    (printout t "На основе ваших ответов: все интересы отсутствуют." crlf)
    (printout t "Возраст: " ?age " лет, Средний балл: " ?grade crlf))

;; Правило 4: Алгоритмическое мышление
(defrule algorithmic-thinking
    (system-state (phase обработка))
    (or (interest (name программирование) (value да))
        (interest (name математика) (value да)))
    =>
    (assert (thinking (name алгоритмическое) (value да))))

;; Правило 5: Аналитическое мышление
(defrule analytical-thinking
    (system-state (phase обработка))
    (or (interest (name математика) (value да))
        (interest (name управление) (value да)))
    =>
    (assert (thinking (name аналитическое) (value да))))

;; Правило 6: Творческое мышление
(defrule creative-thinking
    (system-state (phase обработка))
    (or (interest (name дизайн) (value да))
        (interest (name математика) (value нет)))
    =>
    (assert (thinking (name творческое) (value да))))

;; Правило 7: Усиление творческого мышления (нет математики)
(defrule creative-thinking-enhanced-no-math
    (system-state (phase обработка))
    (interest (name математика) (value нет))
    ?t <- (thinking (name творческое) (value да))
    =>
    (modify ?t (value усилено)))

;; Правило 8: Финансовая грамотность
(defrule financial-literacy-rule
    (system-state (phase обработка))
    (or (interest (name управление) (value да))
        (interest (name экономика) (value да)))
    =>
    (assert (financial-literacy (value да))))

;; Правило 9: Усиление аналитического мышления (нет программирования)
(defrule analytical-thinking-enhanced-no-programming
    (system-state (phase обработка))
    (interest (name программирование) (value нет))
    ?t <- (thinking (name аналитическое) (value да))
    =>
    (modify ?t (value усилено)))

;; Правило 10: Усиление финансовой грамотности (нет аналитического мышления)
(defrule financial-literacy-enhanced-no-analytical
    (system-state (phase обработка))
    (thinking (name аналитическое) (value нет))
    ?f <- (financial-literacy (value да))
    =>
    (modify ?f (value усилено)))

;; Правило 11: Усиление творческого мышления (нет алгоритмического)
(defrule creative-thinking-enhanced-no-algorithmic
    (system-state (phase обработка))
    (thinking (name алгоритмическое) (value нет))
    ?t <- (thinking (name творческое) (value да))
    =>
    (modify ?t (value усилено)))

;; Правило 12: Разработка ИИ
(defrule ai-development
    (system-state (phase обработка))
    (thinking (name аналитическое) (value ?av&да|усилено))
    (thinking (name алгоритмическое) (value ?alg&да))
    =>
    (assert (specialization (name разработка-ИИ) (value да))))

;; Правило 13: Альтернативный путь разработки ИИ
(defrule ai-development-alternative
    (system-state (phase обработка))
    (thinking (name алгоритмическое) (value нет))
    ?s <- (specialization (name разработка-ИИ) (value да))
    =>
    (modify ?s (value альтернативный-путь)))

;; Правило 14: Веб-разработка
(defrule web-development
    (system-state (phase обработка))
    (thinking (name творческое) (value ?tv&да|усилено))
    (thinking (name алгоритмическое) (value ?av&да))
    =>
    (assert (specialization (name веб-разработка) (value да))))

;; Правило 15: Дизайн интерьеров
(defrule interior-design
    (system-state (phase обработка))
    (thinking (name творческое) (value ?v&да|усилено))
    =>
    (assert (specialization (name дизайн-интерьеров) (value да))))

;; Правило 16: Управление проектами
(defrule project-management
    (system-state (phase обработка))
    (financial-literacy (value ?v&да|усилено))
    =>
    (assert (specialization (name управление-проектами) (value да))))

;; Правило 17: Бизнес-аналитика
(defrule business-analytics
    (system-state (phase обработка))
    (financial-literacy (value ?v&да|усилено))
    =>
    (assert (specialization (name бизнес-аналитика) (value да))))

;; Правило 18: Факультет компьютерных наук (через разработку ИИ)
(defrule faculty-computer-science-ai
    (system-state (phase обработка))
    (student-grade (value ?grade&:(>= ?grade 3))) ; Минимальный балл 3
    (specialization (name разработка-ИИ) (value ?ai&да|альтернативный-путь))
    (specialization (name управление-проектами) (value нет))
    =>
    (assert (faculty (name компьютерных-наук) (value да)))
    (assert (result (value "Факультет компьютерных наук"))))

;; Правило 19: Факультет компьютерных наук (через веб-разработку)
(defrule faculty-computer-science-web
    (system-state (phase обработка))
    (student-grade (value ?grade&:(>= ?grade 3))) ; Минимальный балл 3
    (specialization (name веб-разработка) (value да))
    (specialization (name дизайн-интерьеров) (value нет))
    =>
    (assert (faculty (name компьютерных-наук) (value да)))
    (assert (result (value "Факультет компьютерных наук"))))

;; Правило 20: Факультет дизайна (только дизайн интерьеров)
(defrule faculty-design-only
    (system-state (phase обработка))
    (specialization (name дизайн-интерьеров) (value да))
    (specialization (name веб-разработка) (value нет))
    =>
    (assert (faculty (name дизайна) (value да)))
    (assert (result (value "Факультет дизайна"))))

;; Правило 21: Факультет дизайна (дизайн + веб)
(defrule faculty-design-both
    (system-state (phase обработка))
    (specialization (name дизайн-интерьеров) (value да))
    (specialization (name веб-разработка) (value да))
    =>
    (assert (faculty (name дизайна) (value да)))
    (assert (result (value "Факультет дизайна"))))

;; Правило 22: Факультет искусств (только дизайн)
(defrule faculty-arts-only
    (system-state (phase обработка))
    (specialization (name дизайн-интерьеров) (value да))
    (specialization (name веб-разработка) (value нет))
    =>
    (assert (faculty (name искусств) (value да)))
    (assert (result (value "Факультет искусств"))))

;; Правило 23: Факультет искусств (дизайн + веб)
(defrule faculty-arts-both
    (system-state (phase обработка))
    (specialization (name дизайн-интерьеров) (value да))
    (specialization (name веб-разработка) (value да))
    =>
    (assert (faculty (name искусств) (value да)))
    (assert (result (value "Факультет искусств"))))

;; Правило 24: Факультет государственного управления (управление проектами)
(defrule faculty-state-management-pm
    (system-state (phase обработка))
    (student-age (value ?age&:(>= ?age 17))) ; Минимальный возраст 17
    (specialization (name управление-проектами) (value да))
    (specialization (name бизнес-аналитика) (value нет))
    =>
    (assert (faculty (name государственного-управления) (value да)))
    (assert (result (value "Факультет государственного управления"))))

;; Правило 25: Факультет государственного управления (бизнес-аналитика)
(defrule faculty-state-management-ba
    (system-state (phase обработка))
    (student-age (value ?age&:(>= ?age 17))) ; Минимальный возраст 17
    (specialization (name бизнес-аналитика) (value да))
    =>
    (assert (faculty (name государственного-управления) (value да)))
    (assert (result (value "Факультет государственного управления"))))

;; Правило 26: Факультет муниципального управления (оба направления)
(defrule faculty-municipal-management-both
    (system-state (phase обработка))
    (student-age (value ?age&:(>= ?age 18))) ; Минимальный возраст 18
    (specialization (name управление-проектами) (value да))
    (specialization (name бизнес-аналитика) (value да))
    =>
    (assert (faculty (name муниципального-управления) (value да)))
    (assert (result (value "Факультет муниципального управления"))))

;; Правило 27: Факультет муниципального управления (только управление проектами)
(defrule faculty-municipal-management-pm-only
    (system-state (phase обработка))
    (student-age (value ?age&:(>= ?age 18))) ; Минимальный возраст 18
    (specialization (name бизнес-аналитика) (value нет))
    (specialization (name управление-проектами) (value да))
    =>
    (assert (faculty (name муниципального-управления) (value да)))
    (assert (result (value "Факультет муниципального управления"))))

;; Правило 28: Факультет искусств (альтернативный путь)
(defrule faculty-arts-alternative
    (system-state (phase обработка))
    (specialization (name веб-разработка) (value нет))
    (specialization (name дизайн-интерьеров) (value да))
    =>
    (assert (faculty (name искусств) (value да)))
    (assert (result (value "Факультет искусств"))))

;; Правило 29: Альтернативный путь к компьютерным наукам
(defrule computer-science-alternative-path
    (system-state (phase обработка))
    (thinking (name творческое) (value нет))
    ?s <- (specialization (name разработка-ИИ) (value да))
    =>
    (modify ?s (value альтернативный-путь-к-компьютерным-наукам)))

;; Правило 30: Завершение обработки и вывод результата
(defrule processing-complete
    ?state <- (system-state (phase обработка))
    (not (system-state (phase вывод-результата)))
    =>
    (retract ?state)
    (assert (system-state (phase вывод-результата)))
    (print-result)
    (printout t crlf "Для нового расчета выполните (reset) и (run)." crlf))

;; Правило 31: Резервное правило - если не найдено ни одного факультета
(defrule default-faculty
    (system-state (phase вывод-результата))
    (not (result))
    =>
    (assert (result (value "Не удалось определить факультет. Обратитесь к консультанту.")))
    (printout t "Не удалось определить факультет на основе ваших ответов." crlf))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; ЗАПУСК СИСТЕМЫ
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; Инструкции по запуску:
;; 1. Загрузите файл: (load "lab1.clp")
;; 2. Инициализируйте систему: (reset)
;; 3. Добавьте начальное состояние: (assert (system-state (phase начальная)))
;; 4. Запустите систему: (run)
;;
;; Для повторного запуска выполните: (reset), затем (assert (system-state (phase начальная))), затем (run)
