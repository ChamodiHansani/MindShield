import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HelplineSupport } from './helpline-support';

describe('HelplineSupport', () => {
  let component: HelplineSupport;
  let fixture: ComponentFixture<HelplineSupport>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HelplineSupport]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HelplineSupport);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
