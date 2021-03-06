import { NonIdealState, Spinner } from "@blueprintjs/core";
import React, { Component } from "react";
import { Col, Row, Table } from "react-bootstrap";
import { FormattedMessage, defineMessages, injectIntl } from "react-intl";
import { connect } from "react-redux";
import { Link } from "react-router-dom";

import ConfigurationForm from "./ConfigurationForm";
import FilterForm from "./FilterForm";
import Paginator from "./Paginator";
import { getConfigurations, getConfiguration } from "../actions/configurations";
import { selectConfigurations, selectStatus } from "../selectors";

const messages = defineMessages({
  configurationsType: {
    id: "ui.configuration.title",
    defaultMessage: "Configurations"
  }
});

const ConfigurationTable = ({ configurations }) =>
  <tbody>
    {configurations.map((configuration, i) => {
      return (
        <tr key={i}>
          <td>
            <Link to={`/configurations/detail/${configuration.uid}`}>
              {configuration.name}
            </Link>
          </td>
          <td>
            {configuration.description}
          </td>
          <td />
          <td>
            {configuration.user.username}
          </td>
        </tr>
      );
    })}
  </tbody>;

class ConfigurationListPane extends Component {
  state = {
    filters: {}
  };

  componentDidMount() {
    this.props.getConfigurations();
  }

  search = ({ search, ...values }) => {
    const { getConfigurations } = this.props;
    const { filters } = this.state;

    const newFilters = {
      ...filters,
      ...values,
      search
    };

    this.setState({
      filters: newFilters
    });

    return getConfigurations(newFilters);
  };

  render() {
    const {
      configurations,
      getConfigurations,
      intl: { formatMessage },
      status: { loading }
    } = this.props;
    const { filters } = this.props;

    return (
      <Col xs={6} style={{ height: "100%", overflowY: "scroll" }}>
        <div style={{ padding: "20px" }}>
          <h2 style={{ display: "inline" }}>Configurations</h2>
          <Link
            to="/configurations/new"
            style={{ float: "right" }}
            className="btn btn-primary"
          >
            <FormattedMessage
              id="ui.configuration.create"
              defaultMessage="Create New Configuration"
            />
          </Link>
        </div>
        <div style={{ padding: "20px" }}>
          {(configurations.total > 0 || filters !== {}) &&
            <div>
              <FilterForm
                type={formatMessage(messages.configurationsType)}
                onSubmit={this.search}
              />
              {loading &&
                <div>
                  <NonIdealState
                    action={
                      <strong>
                        <FormattedMessage
                          id="ui.loading"
                          defaultMessage="Loading..."
                        />
                      </strong>
                    }
                    visual={<Spinner />}
                  />
                </div>}
              {!loading &&
                configurations.total === 0 &&
                <div>
                  <NonIdealState
                    action={
                      <strong>
                        <FormattedMessage
                          id="ui.no_configurations_found"
                          defaultMessage="No configurations found"
                        />
                      </strong>
                    }
                    visual="warning-sign"
                  />
                </div>}
              {!loading &&
                configurations.total > 0 &&
                <div>
                  <Table>
                    <thead>
                      <tr>
                        <th>
                          <FormattedMessage
                            id="ui.configuration.name.label"
                            defaultMessage="Name"
                          />
                        </th>
                        <th>
                          <FormattedMessage
                            id="ui.configuration.description.label"
                            defaultMessage="Description"
                          />
                        </th>
                        <th>
                          <FormattedMessage
                            id="ui.configuration.tables.label"
                            defaultMessage="Tables"
                          />
                        </th>
                        <th>
                          <FormattedMessage
                            id="ui.configuration.owner.label"
                            defaultMessage="Owner"
                          />
                        </th>
                      </tr>
                    </thead>
                    <ConfigurationTable configurations={configurations.items} />
                  </Table>
                  <Paginator
                    collection={configurations}
                    getPage={getConfigurations.bind(null, filters)}
                  />
                </div>}
            </div>}
        </div>
      </Col>
    );
  }
}

const ConfigurationListPaneContainer = connect(
  state => ({
    configurations: selectConfigurations(state),
    status: selectStatus(state)
  }),
  {
    getConfigurations
  }
)(injectIntl(ConfigurationListPane));

export class ConfigurationNew extends Component {
  render() {
    return (
      <Row style={{ height: "100%" }}>
        <ConfigurationListPaneContainer />
        <Col xs={6} style={{ height: "100%", overflowY: "scroll" }}>
          <div style={{ padding: "20px" }}>
            <ConfigurationForm />
          </div>
        </Col>
      </Row>
    );
  }
}

class ConfigurationDetail extends Component {
  componentDidMount() {
    const { configurationId, getConfiguration } = this.props;

    getConfiguration(configurationId);
  }

  componentWillReceiveProps(props) {
    const { configurationId: prevConfigurationId } = this.props;
    const { configurationId, getConfiguration } = props;

    if (prevConfigurationId !== configurationId) {
      getConfiguration(configurationId);
    }
  }

  render() {
    const { match: { params: { uid } } } = this.props;
    return (
      <Row style={{ height: "100%" }}>
        <ConfigurationListPaneContainer />
        <Col xs={6} style={{ height: "100%", overflowY: "scroll" }}>
          <div style={{ padding: "20px" }}>
            <ConfigurationForm configurationUid={uid} />
          </div>
        </Col>
      </Row>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  configurationId: ownProps.match.params.uid
});

export const ConfigurationDetailContainer = connect(mapStateToProps, {
  getConfiguration
})(ConfigurationDetail);

export class ConfigurationList extends Component {
  render() {
    return (
      <Row style={{ height: "100%" }}>
        <ConfigurationListPaneContainer />
        <Col xs={6} style={{ height: "100%", overflowY: "scroll" }} />
      </Row>
    );
  }
}
