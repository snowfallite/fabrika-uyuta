/** Input mask for the phone field; mirrors tech.md 12.3 step by step. */
export function formatPhoneInput(raw: string): string {
	let digits = raw.replace(/\D/g, '');
	const plus = raw.trimStart().startsWith('+');

	if (!digits) return plus ? '+' : '';
	if (plus && digits[0] !== '7') return '+' + digits.slice(0, 15);

	if (digits[0] === '8') digits = '7' + digits.slice(1);
	else if (digits[0] !== '7') digits = '7' + digits;

	const rest = digits.slice(1, 11);
	let result = '+7';
	if (rest.length > 0) result += ' (' + rest.slice(0, 3);
	if (rest.length > 3) result += ') ' + rest.slice(3, 6);
	if (rest.length > 6) result += '-' + rest.slice(6, 8);
	if (rest.length > 8) result += '-' + rest.slice(8, 10);
	return result;
}
