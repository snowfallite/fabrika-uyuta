import { typo } from '$lib/domain/typo';

// Static home texts from the template (tech.md, appendix A).
export const HERO = typo({
	title: 'Мебель на заказ в Вологде',
	subtitle:
		'Кухни, шкафы, шкафы-купе, кухонные столы и офисная мебель, изготовленные под ваше пространство.',
	cta: 'Оставить заявку',
	secondaryCta: 'Смотреть наши работы'
});

export const CATALOG = typo({
	eyebrow: 'Направления производства',
	title: 'Что мы производим',
	text: 'Изготовляем мебель на заказ для дома и офиса: от кухни до систем хранения.',
	cardCta: 'Оставить заявку'
});

export const WORKS = typo({
	eyebrow: 'Наши работы',
	title: 'Галерея реализованных проектов',
	close: 'Закрыть',
	previous: 'Назад',
	next: 'Вперёд',
	photoTitle: 'Фото работы'
});

export const ABOUT = typo({
	eyebrow: 'О компании',
	title: 'Делаем мебель, которая подходит именно вашему дому',
	// Draft: the template has a placeholder here, the customer supplies the final copy.
	text: 'Проектируем и изготавливаем мебель по размерам вашего помещения. Замер, проект, производство и монтаж делаем сами.',
	points: ['Замер и проект', 'Собственное производство', 'Доставка и сборка', 'Гарантия на изделия']
});

export const MATERIALS = typo({
	eyebrow: 'Материалы',
	title: 'С чем мы работаем',
	items: [
		{
			slot: 'material_ldsp',
			title: 'ЛДСП',
			text: 'Практичный материал для корпусной мебели с широкой палитрой декоров.'
		},
		{
			slot: 'material_mdf',
			title: 'МДФ',
			text: 'Гладкие и фрезерованные фасады для кухонь и шкафов.'
		}
	]
} as const);

export const PROCESS = typo({
	eyebrow: 'Как мы работаем',
	title: 'Путь от заявки до готовой мебели',
	steps: [
		{ title: 'Заявка', text: 'Вы оставляете контакты.' },
		{ title: 'Замер', text: 'Мастер приезжает на объект.' },
		{ title: 'Проект', text: 'Согласуем дизайн и смету.' },
		{ title: 'Производство', text: 'Изготавливаем изделие.' },
		{ title: 'Монтаж', text: 'Доставка и установка.' }
	]
});

export const ADVANTAGES = typo({
	eyebrow: 'Почему выбирают нас',
	title: 'Подход, который виден в деталях',
	items: [
		{ title: 'Точные размеры', text: 'Мебель делается под ваши замеры.' },
		{ title: 'Свой цех', text: 'Контролируем качество на каждом этапе.' },
		{ title: 'Фурнитура', text: 'Надёжные механизмы и аккуратные детали.' },
		{ title: 'Монтаж', text: 'Доставим и соберём на месте.' }
	]
});

export const CONTACTS = typo({
	eyebrow: 'Контакты',
	title: 'Свяжитесь с нами',
	text: 'Позвоните, напишите или оставьте заявку: ответим в рабочее время.',
	phone: 'Телефон',
	email: 'Email',
	address: 'Адрес',
	hours: 'Часы работы',
	map: 'Открыть на карте',
	cta: 'Заказать мебель'
});
