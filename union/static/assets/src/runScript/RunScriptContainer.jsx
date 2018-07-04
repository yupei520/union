import React from 'react';
import { Button, Panel, Grid, Row, Col } from 'react-bootstrap';

const propTypes = {
    bootstrap_data: bootstrap_data
};

const paramList = propTypes.bootstrap_data.keys().map(key => <div>
        <p>{t(key)}</p>
        <Select
            clearable={false}
            name={key}
            value={propTypes.bootstrap_data.get(key)}
        />
    </div>);

export default class RunScriptContainer extends React.PureComponent {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="container">
                <Panel header={<h3>{t('Run Script')}</h3>}>
                    <Grid>
                        <Row>
                            {paramList}
                            <br/>
                            <Button
                                bsStyle="primary"
                                disabled={this.isBtnDisabled()}
                                onClick={this.gotoSlice.bind(this)}
                            >
                                {t('Run Script')}
                            </Button>
                            <br/><br/>
                        </Row>
                    </Grid>
                </Panel>
            </div>
        )
    }
}

RunScriptContainer.propTypes = propTypes;