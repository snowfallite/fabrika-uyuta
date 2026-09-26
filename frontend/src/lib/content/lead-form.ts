import { typo } from '$lib/domain/typo';

// Lead form texts (tech.md, 12.1 and 12.2). Field errors come from the API as is.
export const LEAD_FIELDS = {
	name: { label: 'ФИО', placeholder: 'Иванов Иван Иванович' },
	phone: { label: 'Телефон' },
	product: { label: 'Что хотите заказать', placeholder: 'Выберите' },
	dimensions: { label: 'Примерные размеры', placeholder: 'Стена 3,2 м, высота 2,6 м' },
	comment: { label: 'Комментарий', placeholder: 'Материал, цвет, сроки, пожелания' },
	consent: {
		before: 'Я даю согласие на ',
		link: 'обработку персональных данных'
	}
};

export const LEAD_MESSAGES = typo({
	submit: 'Отправить заявку',
	sending: 'Отправляем…',
	// 12.2 success text, split into a heading line and a note for display.
	successTitle: 'Спасибо! Заявка принята.',
	successText: 'Перезвоним в рабочее время.',
	throttled: 'Слишком много заявок с вашего адреса. Попробуйте позже или позвоните нам.',
	unavailable: 'Не получилось отправить заявку. Попробуйте ещё раз или позвоните нам.',
	again: 'Отправить ещё одну'
});

export const LEAD_SECTION = typo({
	eyebrow: 'Заявка',
	title: 'Расскажите, какая мебель вам нужна',
	text: 'Оставьте контакты: мы свяжемся и обсудим детали вашего проекта.'
});

export const LEAD_PAGE = {
	title: 'Оставить заявку',
	metaTitle: 'Оставить заявку | Фабрика Уюта',
	description: 'Заявка на изготовление мебели на заказ.'
};
