/// <reference types="Cypress" />

describe('the home page', () => {
  it('successfully loads', () => {
    cy.visit('/');
  });

  it('autocompletes for Water', () => {
    cy.visit('/');

    cy.get('.search').type('Water');

    cy.get('.results').should('be.visible');
    cy.get('.results')
      .children('li')
      .eq(1)
      .should('contain.text', 'Water');
  });

  it.only('project-table for Alien displayed', () => {
    cy.visit('/');

    cy.get('.search').type('Water');

    cy.get('.results').should('be.visible');
    cy.get('.results')
      .children('li')
      .eq(1)
      .should('contain.text', 'Water')
      .click();

    cy.get('table').should('be.visible')
      .eq(0)
      .should('contain.text','Water articles by quality and importance')
  });
});