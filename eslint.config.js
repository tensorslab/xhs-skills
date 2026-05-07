import eslint from '@eslint/js'

export default [
  eslint.configs.recommended,
  {
    rules: {
      'no-unused-vars': 'warn',
      'no-undef': 'off',
    },
  },
  {
    ignores: ['node_modules/**', 'demos/**'],
  },
]
