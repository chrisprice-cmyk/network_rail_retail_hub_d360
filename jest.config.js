import { jestConfig } from '@salesforce/sfdx-lwc-jest/config';

export default {
    ...jestConfig,
    modulePathIgnorePatterns: ['<rootDir>/.localdevserver']
};
