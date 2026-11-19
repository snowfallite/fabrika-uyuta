import { typo } from '$lib/domain/typo';

// Static layout texts from the template (tech.md, appendix A).
export const BRAND = 'Фабрика Уюта';
export const LEAD_CTA = 'Оставить заявку';
export const MENU_TITLE = 'Меню';
export const CALL_LABEL = 'Позвонить';
export const SKIP_LINK = 'Перейти к содержанию';
export const BREADCRUMBS = 'Хлебные крошки';

export const FOOTER = typo({
	about:
		'Мебель на заказ для дома и офиса. Кухни, шкафы, столы и системы хранения, изготовленные под ваше пространство.',
	navTitle: 'Навигация',
	leadTitle: 'Заявка',
	leadText: 'Оставьте заявку, и мы обсудим детали вашего будущего изделия.',
	rights: 'Фабрика Уюта. Все права защищены.',
	privacy: 'Политика обработки персональных данных',
	consent: 'Согласие на обработку персональных данных'
});
